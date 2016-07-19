import pandas as pd
import numpy as np
import orca

"""
TO DO
-----
- Instead of 'print' statements, we should log a message if a test passes, and log an
  error if a test fails
- Move this file to its own 'orcatest' library (better name??)
- Incorporate broadcasts and injectables
- Pass a dictionary of data specifications to be evaluated all at once, for example:

    { 'tables':
        [ { 'name': 'table_name',
            'exists': True,
            'columns':
                [ { 'name': 'col1',
                    'exists': True,
                    'index': True },
                  { 'name': 'col2',
                    'exists': False } ]
      'injectables':
        [ { 'name': 'cap_rate',
            'type: 'numeric' } ] }

- Read a dictionary of data specifications from a yaml file
"""


def assert_table_is_registered(table_name):
    """
    Has a table name been registered with orca?
    """
    try:
        assert orca.is_table(table_name)
    except:
        print "Assertion failed: table '%s' is not registered" % table_name + "\n"
        raise
    return


def assert_table_not_registered(table_name):
    """
    """
    try:
        assert not orca.is_table(table_name)
    except:
        print "Assertion failed: table '%s' is already registered" % table_name + "\n"
        raise
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
            print "Assertion failed: table '%s' is registered but cannot be generated" \
                    % table_name + "\n"
            raise
    return


def assert_column_is_registered(column_name, table_name):
    """
    Local columns are registered when their table is evaluated, but stand-alone columns
    can be registered without being evaluated. 
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    try:
        assert (column_name in t.columns) or (column_name == t.index.name)
    except:
        print "Assertion failed: column '%s' is not registered in table '%s'" \
                % (column_name, table_name) + "\n"
        raise
    return


def assert_column_not_registered(table_name, column_name):
    """
    """
    assert_table_can_be_generated(table_name)
    t = orca.get_table(table_name)
    
    try:
        assert (not column_name in t.columns) and (column_name != t.index.name)
    except:
        print "Assertion failed: column '%s' is already registered in table '%s'" \
                % (column_name, table_name) + "\n"
        raise
    return


def assert_column_can_be_generated(table_name, column_name):
    """
    If it's a local column, then it's been generated already when it was registered. If 
    it's a function returning a series, then we need to evaluate it. Does not seem to be 
    possible to do this without getting a copy of the column. And not sure how caching 
    works for computed columns. 
    """
    assert_column_is_registered(column_name, table_name)
    t = orca.get_table(table_name)
    
    # If the requested column is the index, we have to fetch it differently
    # (Missing index does not raise an exception: t.index.name == None)
    if (column_name == t.index.name):
        return
    
    elif (t.column_type(column_name) == 'function'):
        try:
            _ = t.get_column(column_name)
        except:
            print "Assertion failed: column '%s' is registered but cannot be generated" \
                    % column_name + "\n"
            raise
    return


def assert_column_is_unique_index(table_name, column_name):
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
        print "Assertion failed: column '%s' is not set as the index of table '%s'" \
                % (column_name, table_name) + "\n"
        raise
        
    try:
        assert len(idx.unique()) == len(idx)
    except:
        print "Assertion failed: column '%s' is the index of table '%s' but its values are not unique" \
                % (column_name, table_name) + "\n"
        raise
        
    try:
        assert sum(pd.isnull(idx)) == 0
    except:
        print "Assertion failed: column '%s' is the index of table '%s' but it contains missing values" \
                % (column_name, table_name) + "\n"
        raise
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
        print "Assertion failed: column '%s' has type '%s'" \
                % (column_name, type) + "\n"
        raise
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


def assert_missing_value_coding(table_name, column_name, missing_values):
    """
    Asserts that a column's missing entries are coded with a particular value.
    
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
        print "Assertion failed: column '%s' has null entries that are not coded as %s" \
                % (column_name, str(missing_values)) + "\n"
        raise
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
        print "Assertion failed: column '%s' has maximum value %s" \
                % (column_name, str(ds.max())) + "\n"
        raise
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
        print "Assertion failed: column '%s' has minimum value %s" \
                % (column_name, str(ds.min())) + "\n"
        raise
    return


def assert_column_max_portion_missing(table_name, column_name, missing_values=np.nan, portion=0):
    """
    Assert the maximum portion of a column's entries that may be missing.
    
    Parameters
    ----------
    table_name : str
    column_name : str
    missing_values : {0, -1, np.nan}, optional
        Value that indicates missing entires.
    portion : float from 0 to 1
        Maximum portion of entries that may be missing.
    
    Returns
    -------
    none
    
    """
    assert_column_can_be_generated(table_name, column_name)
    ds = get_column_or_index(table_name, column_name)
    missing = len(ds) - len(strip_missing_values(ds, missing_values))
    
    missing_portion = float(missing) / len(ds)
    missing_pct = round(100 * missing_portion, 1)
    
    try:
        assert missing_portion <= portion
    except:
        print "Assertion failed: column '%s' is %s%% missing" \
                % (column_name, missing_pct) + "\n"
        raise
    return


def assert_column_no_missing_values(table_name, column_name, missing_values=np.nan):
    """
    """
    assert_column_max_portion_missing(table_name, column_name, missing_values, 0)
    return






