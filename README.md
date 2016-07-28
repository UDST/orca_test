Orca_test
=========

This is a library of assertions about the characteristics of tables, columns, and injectables that are registered in [Orca](https://github.com/udst/orca). 

The motivation is that [UrbanSim](https://github.com/udst/urbansim) model code expects particular tables and columns to be in place, and can fail unpredictably when data is not as expected (missing columns, NaNs, negative prices, log-of-zero). These failures are rare, but hard to debug, and can happen at any time because data is modified as models run. 

Orca_test assertions can be included in model steps or used as part of the data preparation pipeline. The goal for this library is for it to be useful (1) as a model development aid, (2) for exception handling as simulations run, and (3) for documenting the data specs required by different UrbanSim templates. 


## Installation

Clone this repo and run `python setup.py develop`. Won't be of much use without [Orca](https://github.com/udst/orca) and some project that's using it for simulation orchestration. 


## Usage

You can either make assertions directly by calling individual orca_test functions, or assert a full set of characteristics at once. These characteristics are expressed as nested python classes (similar to sqlalchemy), and in the future will have an equivalent YAML syntax.

If an assertion passes, nothing happens. If it fails, an `OrcaAssertionError` is raised with a detailed message. Orca_test is written to be as computationally efficient as possible, and the main cost will be the generation of tables or columns that have not yet been cached. 

Assertions are chained as necessary: for example, asserting a column's minimum value will automatically assert that it is numeric, that missing values are coded in a particular way (`np.nan` by default), that the column can be generated without errors, and that it is registered with orca.

### Example

```python
import orca_test as ot
from orca_test import OrcaSpec, TableSpec, ColumnSpec

# Define a specification
o_spec = OrcaSpec('my_spec',

	TableSpec('buildings', 
		ColumnSpec('building_id', primary_key=True),
		ColumnSpec('residential_price', numeric=True, min=0)),

	TableSpec('households',
		ColumnSpec('building_id', numeric=True, missing_val=False),
		ColumnSpec('unit_id', missing_val_coding=-1)),
	
	TableSpec('residential_units',
		registered=False))

# Assert the specification
ot.assert_orca_spec(o_spec)
```

### Working demos
- [development_tests.py](https://github.com/urbansim/orca_test/blob/master/development_tests.py) in this repo
- [ual.py](https://github.com/ual/bayarea_urbansim/blob/orca-test/baus/ual.py) in the `orca-test` branch of `UAL/bayarea_urbansim` 


## Full API

There's fairly detailed documentation of individual functions in [orca_test.py](https://github.com/urbansim/orca_test/blob/master/orca_test/orca_test.py).

### Classes
- `OrcaSpec(name [, TableSpec objs, InjectableSpec objs])`
- `TableSpec(table_name [, characteristics, ColumnSpec objs])`
- `ColumnSpec(column_name [, characteristics])`
- `InjectableSpec(injectable_name [, characteristics])` -- not yet implemented
- `OrcaAssertionError`

### Asserting sets of characteristics
- `assert_orca_spec(OrcaSpec)` -- asserts the entire nested spec
- `assert_table_spec(TableSpec)`
- `assert_column_spec(table_name, ColumnSpec)`
- `assert_injectable_spec(InjectableSpec)` -- not yet implemented

### Table assertions

| Argument in TableSpec() | Equivalent low-level function |
| ------------------ | -------------------------------- |
| `registered = True` | `assert_table_is_registered(table_name)` |
| `registered = False` | `assert_table_not_registered(table_name)` |
| `can_be_generated = True` | `assert_table_can_be_generated(table_name)` |

### Column assertions

| Argument in ColumnSpec() | Equivalent low-level function |
| ------------------ | --------------------------------- |
| `registered = True` | `assert_column_is_registered(table_name, column_name)` |
| `registered = False`| `assert_column_not_registered(table_name, column_name)`  |
| `can_be_generated = True`| `assert_column_can_be_generated(table_name, column_name)` |
| `primary_key = True`| `assert_column_is_primary_key(table_name, column_name)` |
| `numeric = True`| `assert_column_is_numeric(table_name, column_name)` |
| `missing_val_coding = {0, -1}`| `assert_column_missing_value_coding` <br> `(table_name, column_name, missing_val_coding)` |
| `max = value`| `assert_column_max` <br> `(table_name, column_name, max [, missing_val_coding])` |
| `min = value`| `assert_column_min` <br> `(table_name, column_name, min [, missing_val_coding])` |
| `max_portion_missing = portion`| `assert_column_max_portion_missing` <br> `(table_name, column_name, portion [, missing_val_coding])` |
| `missing_val = False`| `assert_column_no_missing_values` <br> `(table_name, column_name [, missing_val_coding])` |

Providing a `missing_val_coding` in a `ColumnSpec()` asserts that there are no `np.nan` values in the column. Asserting a `min`, `max`, `max_portion_missing`, or `missing = False` will take into account the `missing_val_coding` that's provided, or else assume that missing values are coded as `np.nan`. 

For example, asserting that a column with values `[2, 3, 3, -1]` has `min = 0` will fail, but asserting that it has  
`min = 0, missing_val_coding = -1` will pass.


## Development wish list
- Add support for broadcasts (foreign keys)
- Add support for injectables
- Add support for specs expressed in YAML
- Write unit tests and set up in Travis
- Make compatible with python 3


## Sample YAML syntax (not yet implemented)

```yaml
- orca_spec:
  - name: my_spec
  
  - table_spec:
    - name: buildings
    - column_spec:
      - name: building_id
  	  - primary_key: True
    - column_spec:
  	  - name: residential_price
  	  - numeric: True
  	  - min: 0
  
  - table_spec:
    - name: households
    - column_spec:
  	  - name: building_id
  	  - numeric: True
  	  - missing_val: False
    - column_spec:
  	  - name: unit_id
  	  - missing_val_coding: -1
  
  - table_spec:
    - name: residential_units
    - registered: False
```


