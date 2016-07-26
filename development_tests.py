"""
This is a script for informal testing of functions as i'm working on them.
"""

import pandas as pd
import numpy as np

import orca
import orca_test as ot



spec = ot.OrcaSpec('spec',

    ot.TableSpec('table1',
		ot.ColumnSpec('building_id', primary_key=True),
		ot.ColumnSpec('residential_price', numeric=True, missing_val_coding=0, min=0)),

    ot.TableSpec('table2', 
        registered=False)
)


print spec.name

for t in spec.tables:
    print t.name
    print t.properties
    
    for c in t.columns:
        print c.name
        print c.properties

