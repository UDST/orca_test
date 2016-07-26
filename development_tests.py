"""
This is a script for informal testing of functions as i'm working on them.
"""

import pandas as pd
import numpy as np

import orca
import orca_test as ot



@orca.table('table1')
def test():
    data = {
        'building_id': [1, 2, 3, 4, 5],
        'strings': ['a','b','c','d','e'],
        'price1': [10, 0, 5, -1, -1],
        'price2': [10, 0, -1, -1, np.nan] }
    df = pd.DataFrame(data).set_index('building_id')
    # t = 5/0
    return df



spec = ot.OrcaSpec('spec',

    ot.TableSpec('table1',
		ot.ColumnSpec('building_id', primary_key=True),
		ot.ColumnSpec('price1', numeric=True, missing_val=False, max=50),
		ot.ColumnSpec('price2', missing_val_coding=np.nan, min=-5),
		ot.ColumnSpec('price1', missing_val_coding=-1, max_portion_missing=0.5)),

    ot.TableSpec('table2', 
        registered=False)
)



ot.assert_orca_spec(spec)

