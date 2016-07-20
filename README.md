orca_test
=========

Assertions for testing the characteristics of orca tables and columns

#### Installation

#### YAML-based table/column specifications

You can assert an entire set of table and column specifications at once, using the following format. Characteristics are mapped to individual assertion statements, which can also be called directly (see next section). 

```python
import orca_test as ot

ot.assert_orca_spec(yaml.load(
"""
- table_name: buildings
  columns:
  - building_id: [index]
  - residential_price: [numeric, missing_val=0, min=0]
  
- table_name: residential_units
  columns:
  - unit_id: [index]
  - unit_residential_price: [numeric, missing_val=0, min=0]
  - unit_residential_rent: [numeric, missing_val=0, min=0]
  - building_id: [numeric, no_missing_val]
  
- table_name: households
  columns:
  - unit_id: [numeric, missing_val=-1]
  - building_id: [numeric, missing_val=-1]
"""))
```

#### Full API


* 

