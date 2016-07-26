"""
This is a script for informal testing of functions as i'm working on them.
"""

import pandas as pd
import numpy as np

import orca
import orca_test as ot



@orca.table('buildings')
def buildings():
    data = {
        'building_id': [1, 2, 3, 4, 5],
        'strings': ['a','b','c','d','e'],
        'price1': [10, 0, 50, -1, -1],
        'price2': [10, 0, -1, -1, np.nan] }
    df = pd.DataFrame(data).set_index('building_id')
    return df

@orca.table('error')
def error():
    e = 5 / 0


# Assertions that pass
spec = ot.OrcaSpec('good_spec',

    ot.TableSpec('buildings',
        registered=False,
        can_be_generated=True),

    ot.TableSpec('buildings',
		ot.ColumnSpec('building_id', primary_key=True),
		ot.ColumnSpec('price1', numeric=True, missing_val=False, max=50),
		ot.ColumnSpec('price2', missing_val_coding=np.nan, min=-5),
		ot.ColumnSpec('price1', missing_val_coding=-1, max_portion_missing=0.5)),

    ot.TableSpec('households', 
        registered=False)
)


ot.assert_orca_spec(spec)


# Assertions that fail

try:
    spec = ot.OrcaSpec('', ot.TableSpec('households', registered=True))
    ot.assert_orca_spec(spec)
    
except AssertionError:
    pass
