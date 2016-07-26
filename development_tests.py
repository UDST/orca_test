"""
This is a script for informal testing of functions as i'm working on them.
"""

import pandas as pd
import numpy as np

import orca
import orca_test as ot
from orca_test import OrcaSpec, TableSpec, ColumnSpec, OrcaAssertionError



@orca.table('buildings')
def buildings():
    data = {
        'building_id': [1, 2, 3, 4, 5],
        'strings': ['a','b','c','d','e'],
        'price1': [10, 0, 50, -1, -1],
        'price2': [10, 0, -1, -1, np.nan] }
    df = pd.DataFrame(data).set_index('building_id')
    return df

@orca.table('badtable')
def badtable():
    e = 5 / 0

@orca.column('buildings', 'badcol')
def badcol():
    e = 5 / 0



# Assertions that should pass

spec = OrcaSpec('good_spec',

    TableSpec('buildings',
        registered=True,
        can_be_generated=True),

    TableSpec('households', 
        registered=False),

    TableSpec('buildings',
		ColumnSpec('building_id', primary_key=True),
		ColumnSpec('price1', numeric=True, missing_val=False, max=50),
		ColumnSpec('price2', missing_val_coding=np.nan, min=-5),
		ColumnSpec('price1', missing_val_coding=-1, max_portion_missing=0.5))
)


ot.assert_orca_spec(spec)



# Assertions that should fail

bad_specs = [
    OrcaSpec('', TableSpec('households', registered=True)),
    OrcaSpec('', TableSpec('buildings', registered=False)),
    OrcaSpec('', TableSpec('badtable', can_be_generated=True)),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('index', registered=True))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', registered=False))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('badcol', can_be_generated=True))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', primary_key=True))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('strings', numeric=True))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price2', missing_val=False))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', max=25))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', min=0))),
    OrcaSpec('', TableSpec('buildings', ColumnSpec('price2', max_portion_missing=0.1))),
]

for bs in bad_specs:

    try:
        ot.assert_orca_spec(bs)
    
    except OrcaAssertionError as e:
        print "OrcaAssertionError: " + str(e)
        pass

