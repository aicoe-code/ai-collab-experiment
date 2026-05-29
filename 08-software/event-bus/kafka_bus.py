"""Kafka event bus — concrete implementation using confluent-kafka.

Implements: FR-030 (Event-Driven Integration), TR-040
Uses confluent-kafka Python client for producer and consumer operations.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from confluent_kafka import Producer, Consumer, KafkaError, KafkaException

from event_bus.base_bus import BaseEventBus, EventHandler
from shared.utils.config import get_settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class KafkaEventBus(BaseEventBus):
    """Kafka-based event bus implementation.

    Supports publishing domain events and subscribing with
    consumer groups for reliable, ordered processing.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._bootstrap_servers = settings.kafka_bootstrap_servers
        self._topic_prefix = settings.kafka_topic_prefix
        self._producer: Producer | None = None
        self._consumers: dict[str, Consumer] = {}
        self._running = False

    def _full_topic(self, topic: str) -> str:
        """Return fully qualified topic name with prefix."""
        return f"{self._topic_prefix}.{topic}"

    async def connect(self) -> None:
        """Initialize Kafka producer."""
        logger.info("Connecting to Kafka: %s", self._bootstrap_servers)
        self._producer = Producer({
            "bootstrap.servers": self._bootstrap_servers,
            "client.id": "cdos-producer",
            "acks": "all",  # Ensure durability
            "enable.idempotence": True,
        })
        self._running = True
        logger.info("Kafka producer connected")

    async def disconnect(self) -> None:
        """Flush and close Kafka producer and consumers."""
        self._running = False

        if self._producer:
            self._producer.flush(timeout=10)
            self._producer = None
            logger.info("Kafka producer disconnected")

        for group_id, consumer in self._consumers.items():
            consumer.close()
            logger.info("Kafka consumer %s closed", group_id)
        self._consumers.clear()

    async def publish(
        self, topic: str, event: dict[str, Any], key: str | None = None
    ) -> None:
        """Publish an event to a Kafka topic.

        Args:
            topic: Logical topic name.
            event: Event payload.
            key: Optional partition key.

        Raises:
            RuntimeError: If producer is not connected.
        """
        if not self._producer:
            raise RuntimeError("Kafka producer not connected")

        full_topic = self._full_topic(topic)
        value = json.dumps(event, default=str).encode("utf-8")
        key_bytes = key.encode("utf-8") if key else None

        def _delivery_callback(err: Any, msg: Any) -> None:
            if err:
                logger.error("Kafka delivery failed for topic %s: %s", full_topic, err)
            else:
                logger.debug(
                    "Kafka message delivered: topic=%s partition=%d offset=%d",
                    msg.topic(), msg.partition(), msg.offset(),
                )

        self._producer.produce(
            topic=full_topic,
            value=value,
            key=key_bytes,
            callback=_delivery_callback,
        )
        self._producer.poll(0)  # Trigger delivery callbacks
        logger.info("Published event to %s (key=%s)", full_topic, key)

    async def subscribe(
        self, topic: str, group_id: str, handler: EventHandler
    ) -> None:
        """Subscribe to a Kafka topic with a consumer group.

        Starts a background polling loop that dispatches messages
        to the handler function.

        Args:
            topic: Logical topic name.
            group_id: Consumer group identifier.
            handler: Async callback for each consumed message.
        """
        full_topic = self._full_topic(topic)
        consumer = Consumer({
            "bootstrap.servers": self._bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        consumer.subscribe([full_topic])
        self._consumers[f"{group_id}:{topic}"] = consumer

        logger.info("Subscribed to %s (group=%s)", full_topic, group_id)

        # Start background consumer loop
        asyncio.create_task(
            self._consume_loop(consumer, full_topic, handler, f"{group_id}:{topic}")
        )

    async def _consume_loop(
        self,
        consumer: Consumer,
        topic: str,
        handler: EventHandler,
        consumer_key: str,
    ) -> None:
        """Background loop for consuming messages."""
        logger.info("Consumer loop started for %s", topic)
        while self._running:
            try:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error("Kafka error on %s: %s", topic, msg.error())
                    continue

                event = json.loads(msg.value().decode("utf-8"))
                try:
                    await handler(event)
                    consumer.commit(msg)
                except Exception as e:
                    logger.error("Handler error for message on %s: %s", topic, e)
                    # TODO: Dead letter queue logic

            except KafkaException as e:
                logger.error("Kafka exception in consume loop: %s", e)
                await asyncio.sleep(1)

        logger.info("Consumer loop stopped for %s", topic)

    async def unsubscribe(self, topic: str, group_id: str) -> None:
        """Unsubscribe a consumer group from a topic."""
        consumer_key = f"{group_id}:{topic}"
        consumer = self._consumers.pop(consumer_key, None)
        if consumer:
            consumer.close()
            logger.info("Unsubscribed %s from %s", group_id, topic)
