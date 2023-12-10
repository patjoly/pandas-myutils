"""
The :mod:`pandas.myutils` My Pandas utility functions
"""

import pandas as pd
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

