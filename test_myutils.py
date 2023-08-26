import pandas as pd
from pandas_myutils.utils import order, idx_toggle_multi, idx_propagate_levels

colnames = [ 'person.id', 'person.fullName.John Doe', 'person.link', 'jerseyNumber',
             'position.code.C', 'position.name.Center', 'stats.skaterStats.goals',
             'stats.skaterStats.assists', 'stats.skaterStats' ]
index_initial = pd.Index( colnames )

tuples_list = [ tuple( colname.split('.') ) for colname in index_initial ]
index_multi = pd.MultiIndex.from_tuples( tuples_list, names=['level_1', 'level_2', 'level_3'] )

# test idx_propagate_levels()

index_propagated = idx_propagate_levels( index_multi )
index_reverted   = idx_propagate_levels( index_propagated, revert=True )
print( index_multi == index_reverted )

# test idx_toggle_multi()

index_toggled    = idx_toggle_multi( index_initial )
index_flattened  = idx_toggle_multi( index_toggled )
print( index_flattened==index_initial  )
print( index_toggled==index_propagated )

breakpoint()

