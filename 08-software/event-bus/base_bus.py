"""Base event bus — abstract interface for event-driven messaging.

Implements: TR-040 (Event-Driven Architecture)
All concrete bus implementations (Kafka, RabbitMQ, etc.) extend this ABC.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

# Type alias for event handler functions
EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class BaseEventBus(ABC):
    """Abstract base class for the event bus.

    Provides publish/subscribe semantics for domain events
    (subject.enrolled, ae.reported, study.activated, etc.).
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the message broker."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the message broker."""

    @abstractmethod
    async def publish(self, topic: str, event: dict[str, Any], key: str | None = None) -> None:
        """Publish an event to a topic.

        Args:
            topic: Topic/channel name (e.g., 'subject.enrolled').
            event: Event payload as a dictionary.
            key: Optional partition key for ordered delivery.
        """

    @abstractmethod
    async def subscribe(
        self, topic: str, group_id: str, handler: EventHandler
    ) -> None:
        """Subscribe to a topic with a consumer group.

        Args:
            topic: Topic to subscribe to.
            group_id: Consumer group identifier.
            handler: Async callback invoked for each message.
        """

    @abstractmethod
    async def unsubscribe(self, topic: str, group_id: str) -> None:
        """Unsubscribe a consumer group from a topic.

        Args:
            topic: Topic to unsubscribe from.
            group_id: Consumer group identifier.
        """
