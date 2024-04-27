"""
The :mod:`pandas.myutils` My Pandas utility functions
"""

import pandas as pd
import pyarrow as pa
import re

def order(df, cols_to_front):
    df = df[ cols_to_front + [ c for c in df if c not in cols_to_front ] ]
    return df

def idx_propagate_levels( idx, revert=False ):
    new_columns = [ [] for _ in range( idx.nlevels ) ]

    if revert==False:
        for level in range( idx.nlevels ):
            level_values = idx.get_level_values( level )
            new_level = []
            for i in range( len(level_values) ):
                if pd.isna( level_values[i] ):
                    new_level.append( new_columns[level - 1][i] )
                else:
                    new_level.append( level_values[i] )
            new_columns[ level ] = new_level

    else:
        for level in range(idx.nlevels - 1, 0, -1):
            level_values = idx.get_level_values(level)
            new_level = []
            for i in range(len(level_values)):
                if level_values[i] == idx.get_level_values(level - 1)[i]:
                    new_level.append(pd.NA)
                else:
                    new_level.append(level_values[i])
            new_columns[level] = new_level

        top_level_values = idx.get_level_values(0)
        new_columns[0] = top_level_values

    new_idx = pd.MultiIndex.from_arrays( new_columns, names=idx.names )
    return new_idx

def idx_toggle_multi( idx, sep='.', propragate=True ):
    if isinstance( idx, pd.MultiIndex ):
        if propragate:
            idx = idx_propagate_levels( idx, revert=True )
        idx_flattened = idx.to_flat_index()
        idx_flattened = [ tuple(subitem for subitem in item if not pd.isna(subitem)) for item in idx_flattened ]
        new_colnames  = [ sep.join(x) for x in idx_flattened ]

        # remove any trailing separators
        if sep=='.':                                # bcs we need to escape the .
            new_colnames = [ re.sub( r'\.*$',    '', x) for x in new_colnames ]
        else:
            new_colnames = [ re.sub( sep + '*$', '', x) for x in new_colnames ]

        new_idx = pd.Index( new_colnames )
    else:
        levels = [ tuple( colname.split( sep ) ) for colname in idx ]
        if not propragate:
            # add empty strings to have tuples of the same length, otherwise from_tuples() will add nan
            max_len = max( len(t) for t in levels )
            for i in range( len(levels) ):
                while len( levels[i] ) < max_len:
                    levels[i] += ('',)

        new_idx = pd.MultiIndex.from_tuples( levels )

        if propragate:
            new_idx = idx_propagate_levels( new_idx )

    return new_idx

def convert_to_integer(df, cols=None, exclude=None, arrow=True):
    if cols==None:
        cols = df.select_dtypes( include='number' ).columns.tolist()

    if exclude:
        cols = [col for col in cols if col not in exclude]

    for col in cols:
        if arrow==True:
            try:
                ser = df[ col ].astype('int64[pyarrow]')
            except pa.lib.ArrowInvalid:
                # TODO: check if ser persists from one loop to another
                pass
            else:
                df[ col ] = ser
                del ser         # not necessary I think but cleaner to delete it I think
        else:
            # arrow=False not implemented yet
            pass
    return df

def convert_to_arrow(df, cols=None, exclude=None, double=False):
    dtype_mapping = {
        'int64':   'int64[pyarrow]',
        'Int64':   'int64[pyarrow]',
        'float64': 'float[pyarrow]',
        'bool':    'bool[pyarrow]',
        'object':  'string[pyarrow]'
    }
    if double==True:
        dtype_mapping['float64'] = 'double[pyarrow]'

    if exclude:
        cols = [col for col in cols if col not in exclude]

    for col in df.columns:
        if not isinstance( df[col].dtype, pd.ArrowDtype ):
            current_dtype = str( df[col].dtype )
            df[col] = df[col].astype( dtype_mapping[current_dtype] )
    return df

