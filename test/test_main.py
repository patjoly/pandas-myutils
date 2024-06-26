import pandas as pd
import numpy as np
from io import StringIO
from pandas_myutils.utils import order, idx_toggle_multi, idx_propagate_levels, convert_to_integer, convert_to_arrow
import pytest

cols_flat = [ 'person.id', 'person.fullName.John Doe', 'person.link', 'jerseyNumber',
             'position.code.C', 'position.name.Center', 'stats.skaterStats.goals',
             'stats.skaterStats.assists', 'stats.skaterStats' ]
cols_mult = [
    ('person', 'id', ''),
    ('person', 'fullName', 'John Doe'),
    ('person', 'link', ''),
    ('jerseyNumber', '', ''),
    ('position', 'code', 'C'),
    ('position', 'name', 'Center'),
    ('stats', 'skaterStats', 'goals'),
    ('stats', 'skaterStats', 'assists'),
    ('stats', 'skaterStats', '')
]
cols_prop= [
    ('person', 'id', 'id'),
    ('person', 'fullName', 'John Doe'),
    ('person', 'link', 'link'),
    ('jerseyNumber', 'jerseyNumber', 'jerseyNumber'),
    ('position', 'code', 'C'),
    ('position', 'name', 'Center'),
    ('stats', 'skaterStats', 'goals'),
    ('stats', 'skaterStats', 'assists'),
    ('stats', 'skaterStats', 'skaterStats')
]

data = {
    'game_id': [2023021027, 2023021027, 2023021027, 2023021028, 2023021028, 2023021028, 2023021029, 2023021029, 2023021029],
    'period': [1, 2, 3, 1, 2, 3, 1, 2, 4],
    'periodType': ['REG', 'REG', 'REG', 'REG', 'REG', 'REG', 'REG', 'REG', 'REG'],
    'away.team': ['STL', 'STL', 'STL', 'NJD', 'NJD', 'NJD', 'WSH', 'WSH', 'WSH'],
    'home.team': ['BOS', 'BOS', 'BOS', 'NYR', 'NYR', 'NYR', 'WPG', 'WPG', 'WPG'],
    'away.goals': [2, 2, 1, 0, 0, 1, 0, 0, 0],
    'home.goals': [0, 0, 1, 0, 2, 1, 1, np.nan, 1],
    'away.shots': [10, 7, 5, 6, 7, 7, 5, 11, 7],
    'home.shots': [12, 12, 13, 12, 8, 6, 12, 8, 9],
    'perc': [.12, .12, .13, .12, .8, .6, np.nan, .8, .9],
    'ot': [False, False, False, False, False, False, False, False, True]
}

# Conventions in this file:
#  - index_* variables:  for fixtures and comparison purposes (i.e. not generated by our functions)
#  - idx_* variables:    generated by our functions

@pytest.fixture(scope='module')
def index_flat():
    yield pd.Index( cols_flat )

@pytest.fixture(scope='module')
def index_mult():
    yield pd.Index( cols_mult )

@pytest.fixture(scope='module')
def index_prop():
    yield pd.Index( cols_prop )

@pytest.fixture(scope='module')
def index_from_tuples(index_flat):
    # the tuples split from a flat index will not be of equal length and from_tuples() will generate nan's for the missing elements
    #  - index_from_tuples is used mostly to test idx_propagate_levels()

    tuples_list = [ tuple( colname.split('.') ) for colname in index_flat ]
    idx = pd.MultiIndex.from_tuples( tuples_list, names=['level_1', 'level_2', 'level_3'] )
    yield idx

@pytest.fixture(scope='module')
def basic_df():
    yield pd.DataFrame( data )

@pytest.fixture(scope='module')
def basic_df_arrow():
    # To do that, I would need to create a temporary file
    df = pd.DataFrame(data)
    csv_string = df.to_csv(index=False)
    df = pd.read_csv( StringIO(csv_string), dtype_backend='pyarrow' )
    yield df

def test_idx_propagate_levels(index_prop, index_from_tuples):
    idx_prop     = idx_propagate_levels( index_from_tuples )
    idx_reverted = idx_propagate_levels( idx_prop, revert=True )
    assert idx_prop.equals(     index_prop )
    assert idx_reverted.equals( index_from_tuples )

def test_idx_toggle_multi_no_propagate(index_flat, index_mult):
    idx_mult          = idx_toggle_multi( index_flat,  propragate=False )
    idx_flat_reverted = idx_toggle_multi( idx_mult,    propragate=False )
    assert idx_mult.equals(          index_mult )
    assert idx_flat_reverted.equals( index_flat )

    idx_flat          = idx_toggle_multi( index_mult,  propragate=False )
    idx_mult_reverted = idx_toggle_multi( idx_flat,    propragate=False )
    assert idx_flat.equals(          index_flat )
    assert idx_mult_reverted.equals( index_mult )

def test_idx_toggle_multi_with_propagate(index_flat, index_prop):
    idx_mult          = idx_toggle_multi( index_flat,  propragate=True )
    idx_flat_reverted = idx_toggle_multi( idx_mult,    propragate=True )
    assert idx_mult.equals(          index_prop )
    assert idx_flat_reverted.equals( index_flat )

    idx_flat          = idx_toggle_multi( index_prop,  propragate=True )
    idx_mult_reverted = idx_toggle_multi( idx_flat,    propragate=True )
    assert idx_flat.equals(          index_flat )
    assert idx_mult_reverted.equals( index_prop )

def test_convert_to_integer(basic_df):
    assert basic_df['home.goals'].dtype == 'float64'
    df = convert_to_integer( basic_df )
    assert df['home.goals'].dtype == 'int64[pyarrow]'

def test_convert_to_integer_with_arrow(basic_df_arrow):
    assert basic_df_arrow['home.goals'].dtype == 'double[pyarrow]'
    df = convert_to_integer( basic_df_arrow )
    assert df['home.goals'].dtype == 'int64[pyarrow]'

def test_convert_to_arrow(basic_df):
    df = convert_to_arrow( basic_df, double=True )
    assert df['ot'].dtype         == 'bool[pyarrow]'
    assert df['perc'].dtype       == 'double[pyarrow]'
    assert df['periodType'].dtype == 'string[pyarrow]'

