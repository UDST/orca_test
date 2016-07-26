import pandas as pd
import numpy as np
import orca

"""
TO DO
-----
- Instead of 'print' statements, we should log a message if a test passes, and log an
  error if a test fails
- Incorporate broadcasts and injectables
- Read a dictionary of data specifications from a yaml file
"""


"""
######################
SPEC CLASS DEFINITIONS
######################

The Spec objects will store (1) characteristics, passed as named arguments, and
(2) sub-objects, passed as unnamed arguments. We may want to specify explicitly in the 
constructors which characteristics and sub-object types are expected, but for now we just 
accept and store anything that's passed in (less code to change as we adjust the API).
"""

class OrcaAssertionError(Exception):
    __module__ = Exception.__module__
    

class OrcaSpec(object):

    def __init__(self, name, *args):
        self.name = name
        self.tables = [t for t in args if isinstance(t, TableSpec)]


class TableSpec(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.columns = [c for c in args if isinstance(c, ColumnSpec)]
        self.properties = kwargs


class ColumnSpec(object):

    def __init__(self, name, **kwargs):
        """
        Parameters
        ----------
        name : str
            Name of column
        
        """
        self.name = name
        self.properties = kwargs



"""
#######################################
FUNCTIONS FOR WORKING WITH SPEC OBJECTS
#######################################
"""

def spec_from_yaml(str):
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
    # Assert the properties of each table
    for t in o_spec.tables:
        assert_table_spec(t)
    
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
    missing_values = np.nan
    for k, v in c_spec.properties.items():
        
        if k == ('missing_val_coding'):
            missing_values = v
            assert_column_missing_value_coding(table_name, c_spec.name, missing_values)
    
    
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

        if (k, v) == ('numeric', True):
            assert_column_is_numeric(table_name, c_spec.name)
            
        if (k, v) == ('missing_val', False):
            assert_column_no_missing_values(table_name, c_spec.name, missing_values)

        if k == 'max':
            assert_column_max(table_name, c_spec.name, v, missing_values)
       
        if k == 'min':
            assert_column_min(table_name, c_spec.name, v, missing_values)
       
        if k == 'max_portion_missing':
            assert_column_max_portion_missing(table_name, c_spec.name, v, missing_values)

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
    try:
        assert orca.is_table(table_name)
    except:
        msg = "Table '%s' is not registered" % table_name
        raise OrcaAssertionError(msg)
    return


def assert_table_not_registered(table_name):
    """
    """
    try:
        assert not orca.is_table(table_name)
    except:
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
    
    if (orca.table_type(table_name) == 'function'):
        try:
            _ = orca.get_raw_table(table_name)._call_func()
        except:
            msg = "Table '%s' is registered but cannot be generated" % table_name
            raise OrcaAssertionError(msg)
    return


def assert_column_is_registered(table_name, column_name):
    """
    Local columns are registered when their table is evaluated, but stand-alone columns
    can be registered without being evaluated. 
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    try:
        assert (column_name in t.columns) or (column_name == t.index.name)
    except:
        msg = "Column '%s' is not registered in table '%s'" % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_not_registered(table_name, column_name):
    """
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    try:
        assert (not column_name in t.columns) and (column_name != t.index.name)
    except:
        msg = "Column '%s' is already registered in table '%s'" % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_can_be_generated(table_name, column_name):
    """
    If it's a local column, then it's been generated already when it was registered. If 
    it's a function returning a series, then we need to evaluate it. Does not seem to be 
    possible to do this without getting a copy of the column. And not sure how caching 
    works for computed columns. 
    """
    assert_column_is_registered(table_name, column_name)
    t = orca.get_table(table_name)
    
    # If the requested column is the index, we have to fetch it differently
    # (Missing index does not raise an exception: t.index.name == None)
    if (column_name == t.index.name):
        return
    
    elif (t.column_type(column_name) == 'function'):
        try:
            _ = t.get_column(column_name)
        except:
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
    none
    
    """
    assert_column_can_be_generated(table_name, column_name)
    
    try:
        idx = orca.get_table(table_name).index
        assert idx.name == column_name
    except:
        msg = "Column '%s' is not set as the index of table '%s'" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
        
    try:
        assert len(idx.unique()) == len(idx)
    except:
        msg = "Column '%s' is the index of table '%s' but its values are not unique" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
        
    try:
        assert sum(pd.isnull(idx)) == 0
    except:
        msg = "Column '%s' is the index of table '%s' but it contains missing values" \
                % (column_name, table_name)
        raise OrcaAssertionError(msg)
    return


def assert_column_matches_other_index(table_name_1, column_name_1, table_name_2, column_name_2, missing_values='np.nan'):
    """
    Maybe this should be done via broadcasts?
    """
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
    
    if (column_name == t.index.name):
        return pd.Series(t.index)
    
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
    none
    
    """
    assert_column_can_be_generated(table_name, column_name)
    type = get_column_or_index(table_name, column_name).dtype
    
    try:
        assert type in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    except:
        msg = "Column '%s' has type '%s' (not numeric)" % (column_name, type)
        raise OrcaAssertionError(msg)
    return


def strip_missing_values(series, missing_values=np.nan):
    """
    Helper function. Returns a pd.Series with missing values stripped.
    
    Parameters
    ----------
    series : pandas.Series
    missing_values : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    series : pandas.Series
    
    """
    if np.isnan(missing_values):
        return series.dropna()
    
    else:
        return series[series != missing_values].copy()


def assert_column_missing_value_coding(table_name, column_name, missing_values):
    """
    Asserts that a column's missing entries are all coded with a particular value.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    missing_values : {0, -1}
        Value that indicates missing entires.
    
    Returns
    -------
    none
    
    """
    assert_column_can_be_generated(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_values)

    try:
        assert sum(pd.isnull(ds)) == 0
    except:
        msg = "Column '%s' has null entries that are not coded as %s" \
                % (column_name, str(missing_values))
        raise OrcaAssertionError(msg)
    return


def assert_column_max(table_name, column_name, max, missing_values=np.nan):
    """
    Asserts a maximum value for a numeric column, ignoring missing values.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    max : int or float
        Maximum value.
    missing_values : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    none
    
    """
    assert_column_is_numeric(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_values)
    
    try:
        assert ds.max() <= max
    except:
        msg = "Column '%s' has maximum value of %s, not %s" \
                % (column_name, str(ds.max()), str(max))
        raise OrcaAssertionError(msg)
    return
    

def assert_column_min(table_name, column_name, min, missing_values=np.nan):
    """
    Asserts a minimum value for a numeric column, ignoring missing values.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    min : int or float
        Minimum value.
    missing_values : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    none
    
    """
    assert_column_is_numeric(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    ds = strip_missing_values(ds, missing_values)
    
    try:
        assert ds.min() >= min
    except:
        msg = "Column '%s' has minimum value of %s, not %s" \
                % (column_name, str(ds.min()), str(min))
        raise OrcaAssertionError(msg)
    return


def assert_column_max_portion_missing(table_name, column_name, portion, missing_values=np.nan):
    """
    Assert the maximum portion of a column's entries that may be missing.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    portion : float from 0 to 1
        Maximum portion of entries that may be missing.
    missing_values : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    
    Returns
    -------
    none
    
    """
    assert_column_can_be_generated(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    missing = len(ds) - len(strip_missing_values(ds, missing_values))
    missing_portion = float(missing) / len(ds)
    
    # Format as percentages for output
    missing_pct = int(round(100 * missing_portion))
    max_pct = int(round(100 * portion))
    
    try:
        assert missing_portion <= portion
    except:
        msg = "Column '%s' is %s%% missing, above limit of %s%%" \
                % (column_name, missing_pct, max_pct)
        raise OrcaAssertionError(msg)
    return


def assert_column_no_missing_values(table_name, column_name, missing_values=np.nan):
    """
    """
    assert_column_max_portion_missing(table_name, column_name, 0, missing_values)
    return






