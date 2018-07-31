Orca_test
=========

[![Build Status](https://travis-ci.org/UDST/orca_test.svg?branch=master)](https://travis-ci.org/UDST/orca_test)

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
		ColumnSpec('residential_price', min=0, missing=False)),

	TableSpec('households',
		ColumnSpec('building_id', foreign_key='buildings.building_id', missing_val_coding=-1)),
	
	TableSpec('residential_units', registered=False),
	
	InjectableSpec('rate', greater_than=0, less_than=1))

# Assert the specification
ot.assert_orca_spec(o_spec)
```

### Working demos
- [development_tests.py](https://github.com/urbansim/orca_test/blob/master/development_tests.py) in this repo
- In the `ual-development` branch of `UAL/bayarea_urbansim`, the model steps include `orca_test` assertions to validate expected data characteristics ([ual.py](https://github.com/ual/bayarea_urbansim/blob/ual-development/baus/ual.py))


## API Reference

There's fairly detailed documentation of individual functions in the [source code](https://github.com/urbansim/orca_test/blob/master/orca_test/orca_test.py).

### Classes
- `OrcaSpec( spec_name, optional TableSpecs, optional InjectableSpecs )`
- `TableSpec( table_name, optional characteristics, optional ColumnSpecs )`
- `ColumnSpec( column_name, optional characteristics )`
- `InjectableSpec( injectable_name, optional characteristics )`
- `OrcaAssertionError`

### Asserting sets of characteristics
- `assert_orca_spec( OrcaSpec )` -- asserts the entire nested spec
- `assert_table_spec( TableSpec )`
- `assert_column_spec( table_name, ColumnSpec )`
- `assert_injectable_spec( InjectableSpec )`

### Table assertions

| Argument in TableSpec() | Equivalent low-level function |
| ------------------ | -------------------------------- |
| `registered = True` | `assert_table_is_registered( table_name )` |
| `registered = False` | `assert_table_not_registered( table_name )` |
| `can_be_generated = True` | `assert_table_can_be_generated( table_name )` |

### Column assertions

| Argument in ColumnSpec() | Equivalent low-level function |
| ------------------ | --------------------------------- |
| `registered = True` | `assert_column_is_registered( table_name, column_name )` |
| `registered = False` | `assert_column_not_registered( table_name, column_name )`  |
| `can_be_generated = True` | `assert_column_can_be_generated( table_name, column_name )` |
| `numeric = True` | `assert_column_is_numeric( table_name, column_name )` |
| `missing_val_coding = np.nan, 0, -1` | `assert_column_missing_value_coding( table_name, column_name, missing_val_coding )` |
| `missing = False`| <code>assert_column_no_missing_values( table_name, column_name, optional&nbsp;missing_val_coding )</code> |
| <code>max_portion_missing&nbsp;=&nbsp;portion</code> | `assert_column_max_portion_missing( table_name, column_name, portion, optional missing_val_coding )` |
| `primary_key = True` | `assert_column_is_primary_key( table_name, column_name )` |
| `foreign_key = 'parent_table_name.parent_column_name'` | <code>assert_column_is_foreign_key( table_name, column_name, parent_table_name, parent_column_name, optional&nbsp;missing_val_coding )</code> |
| `max = value` | <code>assert_column_max( table_name, column_name, maximum, optional&nbsp;missing_val_coding)</code> |
| `min = value` | <code>assert_column_min( table_name, column_name, minimum, optional&nbsp;missing_val_coding )</code> |
| `is_unique = True` | <code>assert_column_is_unique( table_name, column_name )</code> |

#### Notes

Providing a `missing_val_coding` in a `ColumnSpec()` indicates that there should be no `np.nan` values in the column. Assertions involving a `min`, `max`, or `max_portion_missing` will take into account the `missing_val_coding` that's been provided.

For example, asserting that a column with values `[2, 3, 3, -1]` has `min = 0` will fail, but asserting that it has  
`min = 0, missing_val_coding = -1` will pass.

### Injectable assertions

| Argument in InjectableSpec() | Equivalent low-level function |
| ---------------------------- | ----------------------------- |
| `registered = True` | `assert_injectable_is_registered( injectable_name )` |
| `registered = False` | `assert_injectable_not_registered( injectable_name )`  |
| `can_be_generated = True` | `assert_injectable_can_be_generated( injectable_name )` |
| `numeric = True` | `assert_injectable_is_numeric( injectable_name )` |
| `greater_than = value` | `assert_injectable_greater_than( injectable_name, value )` |
| `less_than = value` | `assert_injectable_less_than( injectable_name, value )` |
| `has_key = str` | `assert_injectable_has_key( injectable_name, str )` |


## Development wish list
- Add support for specs expressed in YAML
- Write unit tests and set up in Travis


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
  	  - min: 0
  	  - missing: False
  
  - table_spec:
    - name: households
    - column_spec:
  	  - name: building_id
  	  - foreign_key: buildings.building_id
  	  - missing_val_coding: -1
  
  - table_spec:
    - name: residential_units
    - registered: False
    
  - injectable_spec:
    - name: rate
    - greater_than: 0
    - less_than: 1
```


