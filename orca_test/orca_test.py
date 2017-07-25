# Orca_test
# Copyright (c) 2016 UrbanSim Inc.
# See full license in LICENSE

import numpy as np
import pandas as pd

import orca


"""
######################
SPEC CLASS DEFINITIONS
######################

The Spec objects will store (a) characteristics, passed as named arguments, and
(b) sub-objects, passed as unnamed arguments. For now, we accept and store any named
arguments, regardless of whether they are valid characteristics. (Less code to change
as we adjust the API.)

"""


class OrcaSpec(object):

    def __init__(self, name, *args):
        self.name = name
        self.tables = [t for t in args if isinstance(t, TableSpec)]
        self.injectables = [inj for inj in args if isinstance(inj, InjectableSpec)]


class TableSpec(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.columns = [c for c in args if isinstance(c, ColumnSpec)]
        self.properties = kwargs


class ColumnSpec(object):

    def __init__(self, name, **kwargs):
        self.name = name
        self.properties = kwargs


class InjectableSpec(object):

    def __init__(self, name, **kwargs):
        self.name = name
        self.properties = kwargs


class OrcaAssertionError(Exception):
    """
    This is the exception raised when an assertion from this library fails. 
    
    """
    # The default reporting in logs is "orca_test.OrcaAssertionError", but this line
    # changes that to remove the module name for compactness
    __module__ = Exception.__module__
    

"""
#######################################
FUNCTIONS FOR WORKING WITH SPEC OBJECTS
#######################################
"""


def spec_from_yaml(string):
    return


def assert_orca_spec(o_spec):
    """
    Assert a set of orca data specifications.
    
    Parameters
    ----------
    o_spec : orca_test.OrcaSpec
        Orca data specifications
    
    Returns
    -------
    None
    
    """
    # Assert the properties of each table and injectable
    for t_spec in o_spec.tables:
        assert_table_spec(t_spec)
    
    for i_spec in o_spec.injectables:
        assert_injectable_spec(i_spec)
    
    return


def assert_table_spec(t_spec):
    """
    Assert the properties specified for a table and its columns.
    
    Parameters
    ----------
    t_spec : orca_test.TableSpec
        Table specifications
    
    Returns
    -------
    None
    
    """
    # Translate the table's own properties into assertion statements
    for k, v in t_spec.properties.items():
    
        if (k, v) == ('registered', True):
            assert_table_is_registered(t_spec.name)
        
        if (k, v) == ('registered', False):
            assert_table_not_registered(t_spec.name)
        
        if (k, v) == ('can_be_generated', True):
            assert_table_can_be_generated(t_spec.name)
    
    # Assert the properties of each column
    for c in t_spec.columns:
        assert_column_spec(t_spec.name, c)
        
    return


def assert_column_spec(table_name, c_spec):
    """
    Assert the properties specified for a column.
    
    Parameters
    ----------
    table_name : str
        Name of the orca table containing the column
    c_spec : orca_test.ColumnSpec
        Column specifications
    
    Returns
    -------
    None
    
    """
    # The missing-value coding affects other assertions, so check for this first
    missing_val_coding = np.nan
    for k, v in c_spec.properties.items():
        
        if k == 'missing_val_coding':
            missing_val_coding = v
            assert_column_missing_value_coding(table_name, c_spec.name, missing_val_coding)

    # Translate the column's properties into assertion statements
    for k, v in c_spec.properties.items():
    
        if (k, v) == ('registered', True):
            assert_column_is_registered(table_name, c_spec.name)

        if (k, v) == ('registered', False):
            assert_column_not_registered(table_name, c_spec.name)

        if (k, v) == ('can_be_generated', True):
            assert_column_can_be_generated(table_name, c_spec.name)

        if (k, v) == ('primary_key', True):
            assert_column_is_primary_key(table_name, c_spec.name)

        if k == 'foreign_key':
            # The value should be a str with format 'parent_table_name.parent_column_name'
            tab, col = v.split('.')
            assert_column_is_foreign_key(table_name, c_spec.name, tab, col, missing_val_coding)
       
        if (k, v) == ('numeric', True):
            assert_column_is_numeric(table_name, c_spec.name)
            
        if (k, v) == ('missing', False):
            assert_column_no_missing_values(table_name, c_spec.name, missing_val_coding)

        if k == 'max':
            assert_column_max(table_name, c_spec.name, v, missing_val_coding)
       
        if k == 'min':
            assert_column_min(table_name, c_spec.name, v, missing_val_coding)
       
        if k == 'max_portion_missing':
            assert_column_max_portion_missing(table_name, c_spec.name, v, missing_val_coding)

        if k == 'values_in':
            assert_column_values_in(table_name, c_spec.name, v, missing_val_coding)

        if (k, v) == ('is_unique', True):
            assert_column_is_unique(table_name, c_spec.name)

    return


def assert_injectable_spec(i_spec):
    """
    """
    # Translate the injectable's properties into assertion statements
    for k, v in i_spec.properties.items():
    
        if (k, v) == ('registered', True):
            assert_injectable_is_registered(i_spec.name)

        if (k, v) == ('registered', False):
            assert_injectable_not_registered(i_spec.name)

        if (k, v) == ('can_be_generated', True):
            assert_injectable_can_be_generated(i_spec.name)

        if (k, v) == ('numeric', True):
            assert_injectable_is_numeric(i_spec.name)

        if k == 'greater_than':
            assert_injectable_greater_than(i_spec.name, v)

        if k == 'less_than':
            assert_injectable_less_than(i_spec.name, v)

        if k == 'has_key':
            assert_injectable_has_key(i_spec.name, v)

    return


"""
###################
ASSERTION FUNCTIONS
###################
"""


def assert_table_is_registered(table_name):
    """
    Has a table name been registered with orca?
    """
    if not orca.is_table(table_name):
        msg = "Table '%s' is not registered" % table_name
        raise OrcaAssertionError(msg)
    return


def assert_table_not_registered(table_name):
    """
    """
    if orca.is_table(table_name):
        msg = "Table '%s' is already registered" % table_name
        raise OrcaAssertionError(msg)
    return


def assert_table_can_be_generated(table_name):
    """
    Does a registered table exist as a DataFrame? If a table was registered as a function
    wrapper, this assertion evaluates the function and fails is there are any errors.
    
    In other UrbanSim code, it seem like the accepted way of triggering a table to be 
    evaluated is to run .to_frame() on it. I'm using ._call_func() instead, because I 
    don't need the output and this saves the overhead of copying the DataFrame. Either of
    those methods will be aware of caching, and not regenerate the table if it already
    exists. There no way to tell externally whether a table is cached or not. That might
    be a useful thing to add to the orca API. 
    """
    assert_table_is_registered(table_name)
    
    if orca.table_type(table_name) == 'function':
        try:
            _ = orca.get_raw_table(table_name)._call_func()
        except:
            # TODO: issues #3 log backtrace
            msg = "Table '%s' is registered but cannot be generated" % table_name
            raise OrcaAssertionError(msg)
    return


def assert_column_is_registered(table_name, column_name):
    """
    Local columns are registered when their table is evaluated, but stand-alone columns
    can be registered without being evaluated. 
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    if (column_name not in t.columns) and (column_name not in t.index.names):
        msg = "Column '%s' is not registered in table '%s'" % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_not_registered(table_name, column_name):
    """
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    if (column_name in t.columns) or (column_name in t.index.names):
        msg = "Column '%s' is already registered in table '%s'" % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_can_be_generated(table_name, column_name):
    """
    There are four types of columns: (1) local columns of a registered table, (2) the 
    index of a registered table, (3) SeriesWrapper columns associated with a table, and
    (4) ColumnFuncWrapper columns associated with a table. 
    
    Only the ColumnFuncWrapper columns need to be tested here, because the others already 
    exist at the point when they're registered. 
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_column_is_registered(table_name, column_name)
    t = orca.get_table(table_name)
    
    # t.column_type() fails for index columns, so we have to check for them separately
    if column_name in t.index.names:
        return
    
    elif t.column_type(column_name) == 'function':
        try:
            # This seems to be the only way to trigger evaluation
            _ = t.get_column(column_name)
        except:
            # TODO: issues #3 log backtrace
            msg = "Column '%s' is registered but cannot be generated" % column_name
            raise OrcaAssertionError(msg)
    return


def assert_column_is_primary_key(table_name, column_name):
    """
    Assert that column is the index of the underlying DataFrame, has no missing entires,
    and its values are unique. 
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_column_can_be_generated(table_name, column_name)
    
    idx = orca.get_table(table_name).index
    if len(idx.names) > 1:
        msg = "The table '%s' has a multi-index, and primary key checks are not yet supported." \
                % table_name
        raise OrcaAssertionError(msg)
    if idx.name != column_name:
        msg = "Column '%s' is not set as the index of table '%s'" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
        
    if len(idx.unique()) != len(idx):
        msg = "Column '%s' is the index of table '%s' but its values are not unique" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
        
    if sum(pd.isnull(idx)) != 0:
        msg = "Column '%s' is the index of table '%s' but it contains missing values" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_is_unique(table_name, column_name):
    """
    Assert that column's values are unique. 
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_column_can_be_generated(table_name, column_name)
    
    ds = get_column_or_index(table_name, column_name)
    
    if len(ds.unique()) != len(ds):
        msg = "Column '%s' does not have unique values" \
                % (column_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_is_foreign_key(table_name, column_name, parent_table_name,
                                 parent_column_name, missing_val_coding=np.nan):
    """
    Asserts that a column is a foreign key whose values correspond to the primary key
    column of a parent table. This confirms the integrity of "broadcast" relationships.
    
    For example, if the 'buildings' table has a 'zone_id' column whose values should 
    correspond to the index of the 'zones' table, the former is the foreign key and the 
    latter is the primary key that it matches. You could test for that with:
    
        assert_column_is_foreign_key('buildings', 'zone_id', 'zones', 'zone_id')
    
    The assertion will fail if the foreign key column contains values that are not in the
    primary key column. It does not currently test whether a "broadcast" relationship
    has also been registered between the tables. 
    
    Note that this assertion is fairly strict, and there are valid "broadcast" 
    relationships that would fail it. But it corresponds well to the standard usage.
    
    """
    assert_column_can_be_generated(table_name, column_name)
    assert_column_is_primary_key(parent_table_name, parent_column_name)

    ds_parent = get_column_or_index(parent_table_name, parent_column_name)
    ds_child = get_column_or_index(table_name, column_name)
    # Foreign key in child table may have missing values, but primary key should not
    ds_child = strip_missing_values(ds_child, missing_val_coding)
    
    # Identify values in ds_child that are not in ds_parent
    diff = np.setdiff1d(ds_child.values, ds_parent.values)
    if len(diff) != 0:
        msg = "Column '%s.%s' has values that are not in '%s.%s'" \
                % (table_name, column_name, parent_table_name, parent_column_name)
        if column_name != parent_column_name:
            msg = "Column '%s' has values that are not in '%s'" \
                    % (column_name, parent_column_name)
        raise OrcaAssertionError(msg)
    return


def get_column_or_index(table_name, column_name):
    """
    This generalizes the orca method .get_column(), which fails if you request an index.
    
    Parameters
    ----------
    table_name : str
        Name of table that the column is associated with.
    column_name : str
        Name of a local column, index, SeriesWrapper, or ColumnFuncWrapper.
    
    Returns 
    -------
    series : pandas.Series
    
    """
    assert_column_can_be_generated(table_name, column_name)
    t = orca.get_table(table_name)
    
    if column_name in t.index.names:
        return t.index.get_level_values(column_name).to_series()
    else:
        return t.get_column(column_name)
    

def assert_column_is_numeric(table_name, column_name):
    """
    By default, pandas uses the numpy dtypes 'int64', 'float64', and 'object' (the latter
    for strings or anything else), but it will accept others if explicitly specified. 
    Still need to think through what the use cases will be for the data type assertions.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    
    Returns
    -------
    None
    
    """
    assert_column_can_be_generated(table_name, column_name)
    dtype = get_column_or_index(table_name, column_name).dtype
    
    if dtype not in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
        msg = "Column '%s' has type '%s' (not numeric)" % (column_name, dtype)
        raise OrcaAssertionError(msg)
    return


def strip_missing_values(series, missing_val_coding=np.nan):
    """
    Helper function. Returns a pd.Series with missing values stripped.
    
    Parameters
    ----------
    series : pandas.Series
    missing_val_coding : {0, -1, np.nan}, optional
        Value that indicates missing entries.
    
    Returns
    -------
    series : pandas.Series
    
    """
    if np.isnan(missing_val_coding):
        return series.dropna()
    
    else:
        return series[series != missing_val_coding].copy()


def assert_column_missing_value_coding(table_name, column_name, missing_val_coding):
    """
    Asserts that a column's missing entries are all coded with a particular value.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    missing_val_coding : {0, -1}
        Value that indicates missing entires.
    
    Returns
    -------
    None
    
    """
    assert_column_can_be_generated(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_val_coding)

    if sum(pd.isnull(ds)) != 0:
        msg = "Column '%s' has null entries that are not coded as %s" \
                % (column_name, str(missing_val_coding))
        raise OrcaAssertionError(msg)
    return


def assert_column_max(table_name, column_name, maximum, missing_val_coding=np.nan):
    """
    Asserts a maximum value for a numeric column, ignoring missing values.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    maximum : int or float
    missing_val_coding : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    None
    
    """
    assert_column_is_numeric(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_val_coding)
    
    if not ds.max() <= maximum:
        msg = "Column '%s' has maximum value of %s, not %s" \
                % (column_name, str(ds.max()), str(maximum))
        raise OrcaAssertionError(msg)
    return
    

def assert_column_min(table_name, column_name, minimum, missing_val_coding=np.nan):
    """
    Asserts a minimum value for a numeric column, ignoring missing values.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    minimum : int or float
    missing_val_coding : {0, -1, np.nan}, optional
        Value that indicates missing entries.
    
    Returns
    -------
    None
    
    """
    assert_column_is_numeric(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_val_coding)
    
    if not ds.min() >= minimum:
        msg = "Column '%s' has minimum value of %s, not %s" \
                % (column_name, str(ds.min()), str(minimum))
        raise OrcaAssertionError(msg)
    return


def assert_column_max_portion_missing(table_name, column_name, portion, missing_val_coding=np.nan):
    """
    Assert the maximum portion of a column's entries that may be missing.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    portion : float from 0 to 1
        Maximum portion of entries that may be missing.
    missing_val_coding : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    None
    
    """
    assert_column_can_be_generated(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    missing = len(ds) - len(strip_missing_values(ds, missing_val_coding))
    missing_portion = float(missing) / len(ds)
    
    # Format as percentages for output
    missing_pct = int(round(100 * missing_portion))
    max_pct = int(round(100 * portion))
    
    if not missing_portion <= portion:
        msg = "Column '%s' is %s%% missing, above limit of %s%%" \
                % (column_name, missing_pct, max_pct)
        raise OrcaAssertionError(msg)
    return


def assert_column_no_missing_values(table_name, column_name, missing_val_coding=np.nan):
    """
    """
    assert_column_max_portion_missing(table_name, column_name, 0, missing_val_coding)
    return


def assert_column_values_in(table_name, column_name, values,
                            missing_val_coding=np.nan):
    """
    Asserts that the values in a specified column correspond to a given list
    of acceptable values.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    values : list or str
        List of values or single value to check column against
    missing_val_coding : {0, -1, np.nan}, optional
        Value that indicates missing entries.
    
    Returns
    -------
    None
    
    """

    assert_column_can_be_generated(table_name, column_name)
    
    ds = get_column_or_index(table_name, column_name)
    if type(values) != list:
        values = [values]
    ds_child = get_column_or_index(table_name, column_name)
    # strip missing values from dataset
    ds = strip_missing_values(ds, missing_val_coding)
    
    # Identify values in ds that are not in values list
    diff = np.setdiff1d(ds.values, values)
    if len(diff) != 0:
        msg = "Column {}.{} contains values that are not " \
              "in the acceptable values list: {}".format(table_name, column_name, 
                                                  str(values))
        raise OrcaAssertionError(msg)
    return


def assert_injectable_is_registered(injectable_name):
    """
    """
    if not orca.is_injectable(injectable_name):
        msg = "Injectable '%s' is not registered" % injectable_name
        raise OrcaAssertionError(msg)
    return


def assert_injectable_not_registered(injectable_name):
    """
    """
    if orca.is_injectable(injectable_name):
        msg = "Injectable '%s' is already registered" % injectable_name
        raise OrcaAssertionError(msg)
    return


def assert_injectable_can_be_generated(injectable_name):
    """
    Can an _InjectableFuncWrapper be evaluated without errors?
    
    (The Orca documentation appears inconsistent, but orca.get_injectable() *does* attempt
    to evaluate wrapped functions, and returns the result.)
    
    Parameters
    ----------
    injectable_name : str
    
    Returns
    -------
    None
    
    """
    assert_injectable_is_registered(injectable_name)
    
    if orca.injectable_type(injectable_name) == 'function':
        try:
            _ = orca.get_injectable(injectable_name)
        except:
            # TODO: issues #3 log backtrace
            msg = "Injectable '%s' is registered but cannot be evaluated" % injectable_name
            raise OrcaAssertionError(msg)
    return


def assert_injectable_is_numeric(injectable_name):
    """
    """
    assert_injectable_can_be_generated(injectable_name)
    inj = orca.get_injectable(injectable_name)
    t = type(inj).__name__
    
    if t not in ['int', 'long', 'float']:
        msg = "Injectable '%s' has type '%s' (not numeric)" % (injectable_name, t)
        raise OrcaAssertionError(msg)
    return


def assert_injectable_greater_than(injectable_name, minimum):
    """
    Asserts that a numeric injectable is greater than or equal to a minimum value.
    
    """
    assert_injectable_is_numeric(injectable_name)
    inj = orca.get_injectable(injectable_name)
    
    if not inj >= minimum:
        msg = "Injectable '%s' has value of %s, less than %s" \
                % (injectable_name, str(inj), str(minimum))
        raise OrcaAssertionError(msg)
    return
    

def assert_injectable_less_than(injectable_name, maximum):
    """
    Asserts that a numeric injectable is less than or equal to a maximum value.
    
    """
    assert_injectable_is_numeric(injectable_name)
    inj = orca.get_injectable(injectable_name)
    
    if not inj <= maximum:
        msg = "Injectable '%s' has value of %s, greater than %s" \
                % (injectable_name, str(inj), str(maximum))
        raise OrcaAssertionError(msg)
    return


def assert_injectable_has_key(injectable_name, key):
    """
    """
    assert_injectable_can_be_generated(injectable_name)
    inj = orca.get_injectable(injectable_name)
    
    if not isinstance(inj, dict):
        msg = "Injectable '%s' is not a dict" % injectable_name
        raise OrcaAssertionError(msg)
        
    elif key not in inj:
        msg = "Injectable '%s' does not have key '%s'" % (injectable_name, key)
        raise OrcaAssertionError(msg)
    return
