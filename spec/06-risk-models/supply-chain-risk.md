# Risk Model: Supply Chain

## Overview

| Attribute | Value |
|-----------|-------|
| Risk ID | RISK-SC-001 |
| Category | Supply Chain |
| Severity | HIGH |
| Owner | Clinical Supply Management |
| Review Cycle | Bi-weekly |

Supply chain risk measures the probability that study drug, comparator,
or placebo inventory is insufficient to support ongoing dosing schedules,
or that temperature excursions compromise drug stability. It also covers
biological sample shipment integrity.

---

## Trigger Conditions

Triggers are evaluated against [Entity:Dose], [Entity:Medication],
and [Entity:Sample] data sourced from [System:IWRS] and [System:CTMS].

| ID | Condition | Threshold | Severity |
|----|-----------|-----------|----------|
| SC-T01 | Site-level inventory projected stockout | < 30 days of supply remaining at current dispensing rate | CRITICAL |
| SC-T02 | Country-level inventory depletion | < 60 days of supply at national depot | WARNING |
| SC-T03 | Temperature excursion rate | > 2% of shipments with out-of-range temperature readings | CRITICAL |
| SC-T04 | Drug accountability discrepancy | > 1% of dispensed doses unaccounted for in reconciliation | WARNING |
| SC-T05 | IWRS randomization kit mismatch | > 0 mismatches between shipped and received kits per site | CRITICAL |
| SC-T06 | Comparator drug lot expiry | < 90 days until expiry of any active lot at any site | WARNING |
| SC-T07 | Sample shipment rejection rate | > 5% of biological samples rejected at central lab | WARNING |
| SC-T08 | Labeling error rate | > 0 mislabeled kits detected at any site | CRITICAL |

---

## Detection Method

### Data Sources

- [System:IWRS] — kit inventory, dispensing records, randomization assignments
- [System:CTMS] — shipment tracking, depot inventory, reconciliation logs
- [System:LIMS] — sample receipt, rejection reasons, temperature logs

### Detection Algorithm

```
FOR EACH site IN active_sites:
    # Stockout projection
    avg_dispensing_rate = COUNT(doses_dispensed WHERE last_30_days) / 30
    remaining_kits = SUM(kit_inventory WHERE site_id = site.site_id
                         AND status = 'AVAILABLE')
    days_of_supply = remaining_kits / avg_dispensing_rate

    IF days_of_supply < 30:
        TRIGGER SC-T01

    # Temperature excursion
    total_shipments = COUNT(shipments WHERE last_90_days)
    excursion_shipments = COUNT(shipments WHERE temp_reading
                                NOT BETWEEN temp_min AND temp_max)
    excursion_rate = excursion_shipments / total_shipments * 100

    IF excursion_rate > 2:
        TRIGGER SC-T03

    # Drug accountability
    dispensed = COUNT(doses WHERE status = 'DISPENSED')
    unaccounted = COUNT(doses WHERE status = 'DISPENSED'
                        AND reconciliation_status != 'RECONCILED')
    discrepancy_rate = unaccounted / dispensed * 100

    IF discrepancy_rate > 1:
        TRIGGER SC-T04

    # Sample rejection
    total_samples = COUNT(samples WHERE last_30_days)
    rejected = COUNT(samples WHERE status = 'REJECTED')
    rejection_rate = rejected / total_samples * 100

    IF rejection_rate > 5:
        TRIGGER SC-T07
```

### Monitoring Frequency

| Trigger | Frequency | System |
|---------|-----------|--------|
| SC-T01 | Weekly | [System:IWRS] |
| SC-T02 | Bi-weekly | [System:CTMS] |
| SC-T03 | Per-shipment (event-driven) | [System:CTMS] |
| SC-T04 | Monthly | [System:IWRS], [System:CTMS] |
| SC-T05 | Per-shipment (event-driven) | [System:IWRS] |
| SC-T06 | Monthly | [System:CTMS] |
| SC-T07 | Bi-weekly | [System:LIMS] |
| SC-T08 | Per-kit (event-driven) | [System:IWRS] |

---

## Mitigation Strategy

### SC-T01: Site-Level Stockout Risk

1. Trigger automatic resupply order via [System:IWRS] when stock < 45 days
2. Activate emergency shipment protocol (next-business-day delivery)
3. Redistribute kits from overstocked sites in same country
4. Update dispensing forecasts using real-time enrollment data from [System:CTMS]

### SC-T02: Country-Level Inventory Depletion

1. Initiate manufacturing batch release for additional supply
2. Cross-border redistribution from surplus countries (regulatory permitting)
3. Implement demand-driven manufacturing based on enrollment forecasts
4. Review and adjust min/max inventory levels at national depots

### SC-T03: Temperature Excursions

1. Quarantine affected shipments pending stability assessment
2. Request temperature data logger download from logistics provider
3. Evaluate excursion severity against [Entity:Medication] stability profile
4. If beyond stability limits, destroy affected kits and resupply
5. Issue deviation report to [System:CTMS]

### SC-T05: IWRS Kit Mismatch

1. Immediately halt dispensing at affected site
2. Conduct physical inventory reconciliation
3. If confirmed mismatch, replace kits and document root cause
4. Notify Quality Assurance for investigation

### SC-T07: Sample Shipment Rejection

1. Analyze rejection reasons (temperature, hemolysis, insufficient volume)
2. Retrain site phlebotomists and shipping personnel
3. Upgrade shipping containers if temperature-related rejections persist
4. Implement pre-shipment sample quality checklist

---

## Impact on Data Models

| Affected Entity | Impact | Action |
|-----------------|--------|--------|
| [Entity:Dose] | Dispensing records must reconcile with inventory | Update reconciliation_status |
| [Entity:Medication] | Lot numbers, expiry dates tracked per kit | Add lot tracking attributes |
| [Entity:Sample] | Sample status changes on rejection | Update status to REJECTED |
| [Entity:Subject] | Dosing gaps affect treatment compliance | Flag subjects with missed doses |
| [Entity:Site] | Sites may be suspended for supply issues | Update site status |

### Affected Transforms

- [Transform:EDC→SDTM] — EX (Exposure) domain requires accurate dispensing data
- SDTM CM (Concomitant Medication) domain affected by medication tracking
- Sample shipment data flows through to LB (Lab) domain via [System:LIMS]

### CDISC Impact

| Variable | Domain | Risk Impact |
|----------|--------|-------------|
| EXDOSE, EXDOSU | EX | Inaccurate if dispensing reconciliation fails |
| EXLOT | EX | Lot tracking required for drug accountability |
| CMSTDTC, CMENDTC | CM | Medication dates affected by supply gaps |
| LBREASND | LB | Lab rejection reasons must be captured |
| LBSPEC | LB | Specimen type affected by sample handling |

---

## Escalation Matrix

| Severity | Escalation To | SLA |
|----------|--------------|-----|
| WARNING | Clinical Supply Manager | Review within 5 business days |
| CRITICAL | VP Clinical Operations | Review within 24 hours |
| CRITICAL (temperature excursion) | Quality Assurance Director | Immediate notification |
| CRITICAL (labeling error) | Regulatory Affairs + QA | Immediate notification |

---

## Cross-References

- Related: [Risk:Site] (SC-T01 may trigger site risk evaluation)
- Related: [Risk:Regulatory] (SC-T08 labeling errors have regulatory implications)
- Data source: [System:IWRS], [System:CTMS], [System:LIMS]
- Entities: [Entity:Dose], [Entity:Medication], [Entity:Sample],
  [Entity:Subject], [Entity:Site]
