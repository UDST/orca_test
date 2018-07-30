# Orca_test
# Copyright (c) 2016 UrbanSim Inc.
# See full license in LICENSE

"""
This is an informal set of tests for the various assertions.

"""

from __future__ import print_function

import numpy as np
import pandas as pd

import orca
import orca_test as ot
from orca_test import OrcaSpec, TableSpec, ColumnSpec, InjectableSpec, OrcaAssertionError



@orca.table('buildings')
def buildings():
    data = {
        'building_id': [1, 2, 3, 4, 5],
        'strings': ['a','b','c','d','e'],
        'price1': [10, 0, 50, -1, -1],
        'price2': [10, 0, -1, -1, np.nan],
        'fkey_good': [1, 3, 3, 2, np.nan],
        'fkey_bad': [3, 3, 4, 5, -1] }
    df = pd.DataFrame(data).set_index('building_id')
    return df

@orca.table('zones')
def zones():
    data = {
        'zone_id': [1, 2, 3] }
    df = pd.DataFrame(data).set_index('zone_id')
    return df

@orca.table('badtable')
def badtable():
    e = 5 / 0

@orca.column('buildings', 'badcol')
def badcol():
    e = 5 / 0

orca.add_injectable('dict', {'Berkeley': True})

@orca.injectable('rate')
def rate():
    return round(np.random.random(), 2)

@orca.injectable('bad_inj')
def bad_injectable():
    return 5 / 0


# Assertions that should pass

spec = OrcaSpec('good_spec',

    TableSpec('buildings',
        registered=True,
        can_be_generated=True),

    TableSpec('households', 
        registered=False),

    TableSpec('buildings',
		ColumnSpec('building_id', primary_key=True),
		ColumnSpec('price1', numeric=True, missing=False, max=50),
		ColumnSpec('price2', missing_val_coding=np.nan, min=-5),
		ColumnSpec('price1', missing_val_coding=-1, max_portion_missing=0.5),
		ColumnSpec('fkey_good', foreign_key='zones.zone_id')),
		
	InjectableSpec('dict', has_key='Berkeley'),
	InjectableSpec('rate', greater_than=0, less_than=1),
	InjectableSpec('bad_inj', registered=True),
	InjectableSpec('nonexistent', registered=False)
)


ot.assert_orca_spec(spec)



# Assertions that should fail

bad_specs = [
#     OrcaSpec('', TableSpec('households', registered=True)),
#     OrcaSpec('', TableSpec('buildings', registered=False)),
#     OrcaSpec('', TableSpec('badtable', can_be_generated=True)),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('index', registered=True))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', registered=False))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('badcol', can_be_generated=True))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', primary_key=True))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('strings', numeric=True))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price2', missing=False))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', max=25))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price1', min=0))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('price2', max_portion_missing=0.1))),
#     OrcaSpec('', TableSpec('buildings', ColumnSpec('fkey_bad', foreign_key='zones.zone_id'))),
#     OrcaSpec('', InjectableSpec('nonexistent', registered=True)),
#     OrcaSpec('', InjectableSpec('rate', registered=False)),
#     OrcaSpec('', InjectableSpec('bad_inj', can_be_generated=True)),
#     OrcaSpec('', InjectableSpec('dict', numeric=True)),
#     OrcaSpec('', InjectableSpec('rate', greater_than=5)),
#     OrcaSpec('', InjectableSpec('rate', less_than=-5)),
#     OrcaSpec('', InjectableSpec('rate', has_key='Berkeley')),
#     OrcaSpec('', InjectableSpec('dict', has_key='Oakland')),
]

for bs in bad_specs:
    try:
        ot.assert_orca_spec(bs)
    except OrcaAssertionError as e:
        print("OrcaAssertionError: " + str(e))
        pass

