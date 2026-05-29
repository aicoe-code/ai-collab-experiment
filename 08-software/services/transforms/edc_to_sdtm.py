"""EDC to SDTM Transform — maps CDASH/EDC data to CDISC SDTM domains.

Implements: FR-025 (CDISC SDTM Mapping), TR-030
Supports: DM (Demographics), AE (Adverse Events), LB (Lab), EX (Exposure), CM (Concomitant Meds)
Standard: CDISC SDTM v3.4
"""

from __future__ import annotations

from typing import Any
from datetime import datetime

from services.transforms.base_transform import BaseTransform
from shared.utils.logging import get_logger
from shared.utils.errors import ValidationError

logger = get_logger(__name__)

# SDTM domain code mappings
_DOMAIN_MAPPINGS: dict[str, dict[str, str]] = {
    "DM": {
        "description": "Demographics",
        "cdash_fields": "USUBJID, SUBJID, SITEID, AGE, SEX, RACE, ETHNIC",
        "sdtm_variables": "STUDYID, DOMAIN, USUBJID, SUBJID, SITEID, AGE, SEX, RACE, ETHNIC",
    },
    "AE": {
        "description": "Adverse Events",
        "cdash_fields": "AETERM, AESEV, AESER, AESTDTC, AEENDTC, AEOUT",
        "sdtm_variables": "STUDYID, DOMAIN, USUBJID, AESEQ, AETERM, AEDECOD, AESEV, AESER, AESTDTC, AEENDTC, AEOUT",
    },
    "LB": {
        "description": "Laboratory Test Results",
        "cdash_fields": "LBTESTCD, LBTEST, LBORRES, LBORRESU, LBSTDTC",
        "sdtm_variables": "STUDYID, DOMAIN, USUBJID, LBSEQ, LBTESTCD, LBTEST, LBORRES, LBORRESU, LBSTRESC, LBSTRESN, LBSTRESU, LBDTC, LBNRIND",
    },
    "EX": {
        "description": "Exposure",
        "cdash_fields": "EXTRT, EXDOSE, EXDOSU, EXSTDTC, EXENDTC",
        "sdtm_variables": "STUDYID, DOMAIN, USUBJID, EXSEQ, EXTRT, EXDOSE, EXDOSU, EXSTDTC, EXENDTC",
    },
    "CM": {
        "description": "Concomitant Medications",
        "cdash_fields": "CMTRT, CMDOSE, CMDOSU, CMSTDTC, CMENDTC",
        "sdtm_variables": "STUDYID, DOMAIN, USUBJID, CMSEQ, CMTRT, CMDECOD, CMDOSE, CMDOSU, CMSTDTC, CMENDTC",
    },
}


class EDCtoSDTMTransform(BaseTransform):
    """Transform EDC (CDASH) data to CDISC SDTM v3.4 format.

    Handles field name mapping, controlled terminology translation,
    date formatting, and derived variable computation.
    """

    def __init__(self, domain: str = "DM") -> None:
        """Initialize transform for a specific SDTM domain.

        Args:
            domain: 2-character SDTM domain code (DM, AE, LB, EX, CM).
        """
        if domain not in _DOMAIN_MAPPINGS:
            raise ValueError(
                f"Unsupported SDTM domain: {domain}. "
                f"Supported: {', '.join(_DOMAIN_MAPPINGS.keys())}"
            )
        self._domain = domain

    @property
    def source_format(self) -> str:
        return "CDASH/EDC"

    @property
    def target_format(self) -> str:
        return f"SDTM/{self._domain}"

    async def validate_input(self, data: dict[str, Any]) -> list[str]:
        """Validate EDC input data has required CDASH fields.

        Args:
            data: EDC source data.

        Returns:
            List of validation error messages.
        """
        errors: list[str] = []
        mapping = _DOMAIN_MAPPINGS[self._domain]
        required_fields = [f.strip() for f in mapping["cdash_fields"].split(",")]

        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required CDASH field: {field}")

        # Date format validation
        for key, value in data.items():
            if key.endswith("DTC") and value:
                try:
                    datetime.fromisoformat(str(value))
                except ValueError:
                    errors.append(f"Invalid ISO date format for {key}: {value}")

        return errors

    async def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform a single EDC record to SDTM format.

        Args:
            data: CDASH source record.

        Returns:
            SDTM-formatted record.

        Raises:
            ValidationError: If transformation fails.
        """
        errors = await self.validate_input(data)
        if errors:
            raise ValidationError(
                f"Input validation failed for {self._domain} transform",
                errors=[{"field": "input", "message": e} for e in errors],
            )

        logger.debug("Transforming %s record to SDTM", self._domain)

        result: dict[str, Any] = {
            "STUDYID": data.get("STUDYID", ""),
            "DOMAIN": self._domain,
        }

        # Apply domain-specific transformations
        if self._domain == "DM":
            result.update(self._transform_dm(data))
        elif self._domain == "AE":
            result.update(self._transform_ae(data))
        elif self._domain == "LB":
            result.update(self._transform_lb(data))
        else:
            result.update(self._transform_generic(data))

        result["_transformed_at"] = datetime.utcnow().isoformat()
        result["_source_format"] = "CDASH"
        result["_target_format"] = f"SDTM/{self._domain}"

        return result

    async def transform_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform a batch of EDC records to SDTM.

        Args:
            records: List of CDASH source records.

        Returns:
            List of SDTM-formatted records.
        """
        results: list[dict[str, Any]] = []
        for record in records:
            try:
                transformed = await self.transform(record)
                results.append(transformed)
            except ValidationError as e:
                logger.warning(
                    "Skipping record due to validation error: %s", e.message
                )
        logger.info(
            "Batch transform %s: %d/%d records successful",
            self._domain, len(results), len(records),
        )
        return results

    def _transform_dm(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform Demographics (DM) domain fields."""
        return {
            "USUBJID": f"{data.get('STUDYID', '')}-{data.get('SUBJID', '')}",
            "SUBJID": data.get("SUBJID", ""),
            "SITEID": data.get("SITEID", ""),
            "AGE": data.get("AGE"),
            "SEX": data.get("SEX", ""),
            "RACE": data.get("RACE", ""),
            "ETHNIC": data.get("ETHNIC", ""),
            "COUNTRY": data.get("COUNTRY", ""),
        }

    def _transform_ae(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform Adverse Events (AE) domain fields."""
        return {
            "USUBJID": f"{data.get('STUDYID', '')}-{data.get('SUBJID', '')}",
            "AESEQ": data.get("AESEQ"),
            "AETERM": data.get("AETERM", ""),
            "AEDECOD": data.get("AEDECOD", ""),  # MedDRA preferred term
            "AESEV": self._map_severity(data.get("AESEV", "")),
            "AESER": data.get("AESER", ""),
            "AESTDTC": data.get("AESTDTC", ""),
            "AEENDTC": data.get("AEENDTC", ""),
            "AEOUT": data.get("AEOUT", ""),
        }

    def _transform_lb(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform Lab Results (LB) domain fields."""
        return {
            "USUBJID": f"{data.get('STUDYID', '')}-{data.get('SUBJID', '')}",
            "LBSEQ": data.get("LBSEQ"),
            "LBTESTCD": data.get("LBTESTCD", ""),
            "LBTEST": data.get("LBTEST", ""),
            "LBORRES": data.get("LBORRES", ""),
            "LBORRESU": data.get("LBORRESU", ""),
            "LBSTRESC": data.get("LBSTRESC", ""),  # standardized result
            "LBSTRESN": data.get("LBSTRESN"),  # numeric result
            "LBSTRESU": data.get("LBSTRESU", ""),  # standardized unit
            "LBDTC": data.get("LBDTC", ""),
            "LBNRIND": data.get("LBNRIND", ""),  # normal range indicator
        }

    def _transform_generic(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generic transform: pass through fields with SDTM variable names."""
        mapping = _DOMAIN_MAPPINGS[self._domain]
        sdtm_vars = [v.strip() for v in mapping["sdtm_variables"].split(",")]
        result: dict[str, Any] = {}
        for var in sdtm_vars:
            if var in data:
                result[var] = data[var]
        return result

    @staticmethod
    def _map_severity(value: str) -> str:
        """Map CDASH severity to SDTM severity controlled terminology."""
        mapping = {
            "MILD": "MILD",
            "MODERATE": "MODERATE",
            "SEVERE": "SEVERE",
        }
        return mapping.get(value.upper(), value)
