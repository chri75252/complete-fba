# Preflight calibration (v1.1)

- Source: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx`
- Sample rows: `200`
- Detected supplier domain: `efghousewares.co.uk`

## Calibration configuration

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pcs', 'pk', 'pack', 'bag', 'box', 'capsule', 'case', 'each', 'pair', 'stick', 'tablet'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'mm', 'ml', 'ltr', 'kg', 'g', 'oz', 'inch', 'l', 'ft', 'in', 'm', 'x'],
    "brand_position": 'start',
    "sales_column": 'bought_in_past_month',
    "capacity_pattern_as_rsu": False,
}
# ---------------------------------
```

## Calibration warnings (sample)

- Row 157: 'SUNNEX STAINLESS STEEL TABLE FORKS PK12 05/11' should treat date/code suffix as reference, not pack quantity
- Row 22: 'PK6' should be RSU=6 (pack qty), not RSU=1
- Row 48: 'PK8' should be RSU=8 (pack qty), not RSU=1
- Row 157: 'PK12' should be RSU=12 (pack qty), not RSU=1
- Row 175: 'PK20' should be RSU=20 (pack qty), not RSU=1
- Row 187: 'PK3' should be RSU=3 (pack qty), not RSU=1
- Row 1: 'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3' should be RSU=1 (variant/age/number), not RSU=3
- Row 19: 'PARTY CRAZY BALLOONS ASSORTED 20' likely indicates pack qty RSU=20, not RSU=1
- Row 35: 'UNIQUE CANDLE NUMBER W/DECOR 6' likely indicates pack qty RSU=6, not RSU=1
- Row 107: 'UNIQUE CANDLE NUMBER W/DECOR 8' likely indicates pack qty RSU=8, not RSU=1
- Row 142: 'UNIQUE BALLOON ASSORTED COLOUR MIX 50TH BIRTHDAY  10' likely indicates pack qty RSU=10, not RSU=1
- Row 156: 'BALLOONS HAPPY BIRTHDAY 12' likely indicates pack qty RSU=12, not RSU=1
- Row 159: 'DUNLOP BIKE SPOKE WRENCH 10-15' should be RSU=1 (size range), not RSU=15
- Row 160: 'BALLOONS SILVER 20' likely indicates pack qty RSU=20, not RSU=1
- Row 162: 'LUXURY PETS BIRTHDAY CARDS 8' likely indicates pack qty RSU=8, not RSU=1
- Row 7: 'STATUS LED G9 2W LED CAPSULE BULB EACH' should not infer RSU without a nearby quantity, not default to a random qty
- Row 11: 'EASY STORAGE VACUUM BAG 70X100CM' should not infer RSU without a nearby quantity, not default to a random qty
- Row 24: 'DLUX WASHING BAG' should not infer RSU without a nearby quantity, not default to a random qty
- Row 63: 'BIRDBRAND S/WASH R/T/USE EACH 5LT' should not infer RSU without a nearby quantity, not default to a random qty
- Row 67: 'ADORN FOLDING BAG ASSORTED COLOURS' should not infer RSU without a nearby quantity, not default to a random qty
- Row 11: 'EASY STORAGE VACUUM BAG 70X100CM' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 37: 'SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 56: 'PALOMA 2PLY IVORY 50 NAPKINS 40X40CM' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 69: 'NORTHPOLE CURLING RIBBON 4 X 4M' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 82: 'LAUNDRY BAG HUL LARGE 70X55X23CM ASSORTED' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 167: 'MATANA 40 Premium White Plastic Plates with Gold Lace Rim - 20x 26cm Dinner Plat' should treat NxM as dimensions, not RSU=multiplied dimensions
- Row 187: '100 x Incontinence Bed Pads | Disposable Bed Pads | Bed Protectors For Incontine' should treat NxM as dimensions, not RSU=multiplied dimensions
