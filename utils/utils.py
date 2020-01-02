import pandas as pd
import numpy as np

def convert_elapsed_time(col):
    '''
    Function converts date column (either 8- or 4-digits) to pd datetime format, then
    to elapsed days since Unix date
    :col: pandas series
    Returns pandas series in elapsed days since Unix date
    '''
    # Convert to standard pandas datetime
    test = pd.to_datetime(col, format='%Y%m%d', errors='coerce') # YYYYMMDD
    if test.isnull().mean() == 1: # wrong format
        test = pd.to_datetime(col, format='%y%m', errors='coerce') # YYMM
        if test.isnull().mean() == 1:
            test = pd.to_datetime(col, format='%d%b%y', errors='coerce') # e.g. 30Jan10
            if test.isnull().mean() == 1:
                raise ValueError("\nDate formatting of {} unclear".format(col))
            else:
                col = test
        else:
            col = test
    else:
        col = test

    # Convert to days since Unix date
    col = (col - pd.to_datetime('1970-01-01', format='%Y-%m-%d')).astype('timedelta64[D]')
    return col

def del_invar_miss_col(df, thresh=0.95, view=False):
    '''
    Function drops columns more than 95% missing and invariant columns.
    :df: pandas data frame
    :thresh: float, proportion of column missing
    :view: bool, if true prints col name deleted
    Returns dataframe minus mostly missing or invariant columns.
    '''
    for col in df.columns:

        df[col].replace('', np.NaN, inplace=True)

        if df[col].isnull().mean() > thresh:
            if view:
                print(col, 'was >{}% missing and deleted'.format(thresh))
            del df[col]
        else: # verify not invariant if not mostly missing
            if len(df[df[col].notnull()][col].unique()) == 1:
                if view:
                    print(col, 'was invariant and deleted')
                del df[col]
    return df

def factorize_columns(df):
    '''
    Converts all object-type columns in pandas dataframe to intergers.
    :df: pandas dataframe
    returns: dictionary of integer mappings back to original strings and modified dataframe
    '''

    dictionary = {} # initialize dictionary for factor mappings

    cols = [i for i in list(df.select_dtypes(include=['object']).columns) if 'Candidate' not in i]
    for col in cols:
        num_codes = df[col].astype('category').cat.codes.drop_duplicates().to_list() # NaN is -1
        orig_codes = df[col].drop_duplicates().to_list()
        dictionary[col] = dict(zip(num_codes, orig_codes))
        df[col] = df[col].astype('category').cat.codes
    return dictionary, df

def list_series(lst):
    '''
    Iterates through a list of lists in a Pandas series,
    converting each element to string
    :lst: pandas series as list
    returns: string series
    '''
    s = pd.Series()
    for nr in range(0, len(lst)):
        try:
            row = pd.Series(', '.join(str(x) for x in lst[nr]))
        except TypeError:
            row = pd.Series('')
        s = s.append(row, ignore_index=True)
    return s.reset_index(drop=True).replace('', np.NaN)