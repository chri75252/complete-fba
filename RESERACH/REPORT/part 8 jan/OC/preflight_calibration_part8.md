# Preflight calibration (v1.1)

- Source: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx`
- Sample rows: `50`
- Detected supplier domain: `efghousewares.co.uk`

## Calibration configuration

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pcs', 'pk', 'bag', 'box', 'capsule', 'case', 'each', 'stick', 'tablet'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'mm', 'ml', 'ltr', 'kg', 'g', 'oz', 'inch', 'l', 'in', 'm', 'x'],
    "brand_position": 'start',
    "sales_column": 'bought_in_past_month',
    "capacity_pattern_as_rsu": False,
}
# ---------------------------------
```

## Calibration warnings (sample)

- Row 2: 'PK6' should be RSU=6 (pack qty), not RSU=1
- Row 3: 'PK8' should be RSU=8 (pack qty), not RSU=1
- Row 25: 'PK24' should be RSU=24 (pack qty), not RSU=1
- Row 46: 'PK6' should be RSU=6 (pack qty), not RSU=1
- Row 4: 'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3' should be RSU=1 (variant/age/number), not RSU=3
- Row 30: 'BAUER STRAIGHTENER BRUSH 38820 BLACK 21.04' likely indicates pack qty RSU=4, not RSU=1
- Row 24: 'LONDON FRAGRANCES FOR HER ENGLISH PEAR & FREESIA 100ML EACH' should not infer RSU without a nearby quantity, not default to a random qty
- Row 29: 'LONDON FRAGRANCES FOR HIM POMEGRANATE NOIR 100ML EACH' should not infer RSU without a nearby quantity, not default to a random qty
- Row 33: 'EASY STORAGE VACUUM BAG 70X100CM' should not infer RSU without a nearby quantity, not default to a random qty
- Row 36: 'STATUS LED G9 2W LED CAPSULE BULB EACH' should not infer RSU without a nearby quantity, not default to a random qty
- Row 37: 'BIRDBRAND S/WASH R/T/USE EACH 5LT' should not infer RSU without a nearby quantity, not default to a random qty
- Row 33: 'EASY STORAGE VACUUM BAG 70X100CM' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 26: 'ONYA DINNER SET 16 PIECES 4 MUGS 4 BOWLS 4 DINNER PLATES 4 SIDE PLATES SEIZE THE' should treat repeated trailing number as code, not pack quantity
