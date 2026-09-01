# Part 3B - Disclosure Extraction Output (MOCK_LLM=True)

## doc_01

> doc_01: Assuming input costs remain stable through the next two quarters, we expect margins to hold at current levels.

- risk_flags: []
- hedging_detected: True
- sentiment: cautious

## doc_02

> doc_02: The company faces an ongoing litigation matter related to a former vendor contract; management believes the exposure is not material.

- risk_flags: ['litigation risk']
- hedging_detected: False
- sentiment: neutral

## doc_03

> doc_03: Our top three customers together account for approximately 42 percent of total revenue this year.

- risk_flags: ['customer concentration risk']
- hedging_detected: False
- sentiment: neutral

## doc_04

> doc_04: We remain cautiously optimistic about demand recovery, though visibility beyond the next quarter is limited given macro uncertainty.

- risk_flags: []
- hedging_detected: True
- sentiment: cautious

## doc_05

> doc_05: The board is confident in the long-term strategy and has approved an expanded capital expenditure plan for the coming year.

- risk_flags: []
- hedging_detected: False
- sentiment: confident

## doc_06

> doc_06: A recent regulatory notice has been received regarding data-localization compliance; the company is in active dialogue with the regulator.

- risk_flags: ['regulatory risk']
- hedging_detected: False
- sentiment: neutral
