orca_test
=========

Assertions for testing the characteristics of `orca` tables and columns. Two primary use cases are anticipated:

- UrbanSim model steps can include assertions about the orca tables and columns that are required for it to run. 

- Each UrbanSim template can include an associated initial data specification.


## Installation

Clone this repo and run `python septup develop`.

For an implementation example, you can look at the `orca-test` branch of `UAL/bayarea_urbansim` ([here](https://github.com/ual/bayarea_urbansim/blob/orca-test/baus/ual.py)).


## YAML-based table/column specifications

You can assert an entire set of table and column specifications at once, using the following format. Characteristics are mapped to individual assertion statements, which can also be called directly (see next section). 

```python
import orca_test as ot

ot.assert_orca_spec(yaml.load(
"""
- table_name: buildings
  columns:
  - building_id: [index]
  - residential_price: [numeric, missing_val=0, min=0]
  
- table_name: households
  columns:
  - building_id: [numeric, no_missing_val]
  - unit_id: [not_registered]

- table_name: residential_units
  characteristics: [not_registered]
"""))
```


## Full API

Each function maps to a keyword that can be included in a yaml specification. 

Note that the assertion functions call each other hierarchically as needed: for example, asserting that a column is registered will also assert that its associated table can be generated. 

The current API is a work in progress.

#### Table assertions
- `assert_table_is_registered(table_name)`
- `assert_table_not_registered(table_name)`
- `assert_table_can_be_generated(table_name)`

#### Column assertions
- `assert_column_is_registered(table_name, column_name)`
- `assert_column_not_registered(table_name, column_name)`
- `assert_column_can_be_generated(table_name, column_name)`
- `assert_column_is_unique_index(table_name, column_name)`
- `assert_column_is_numeric(table_name, column_name)`
- `assert_column_missing_value_coding(table_name, column_name, missing_values)`
- `assert_column_max(table_name, column_name, max, missing_values=np.nan)`
- `assert_column_min(table_name, column_name, min, missing_values=np.nan)`
- `assert_column_max_portion_missing(table_name, column_name, portion, missing_values=np.nan)`
- `assert_column_no_missing_values(table_name, column_name, missing_values=np.nan)`





