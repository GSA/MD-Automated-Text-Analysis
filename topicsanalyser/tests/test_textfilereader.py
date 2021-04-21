import pytest
from ..textfilereader import TextFileReader
import pandas as pd
import collections

@pytest.fixture
def input_df():
    df_in = pd.DataFrame({'Other_Col1':['Value 1','Value 2'], 'Other_Col2':[1, 2], 'Articles':['Some texts', 'Other texts']})
    return df_in

def test_init():
    file = '/usr/someone/myfile.csv'
    reader = TextFileReader(file)
    assert reader.data_file_path == file    
    
def test_read_data_exception():
    with pytest.raises(ValueError):
        reader = TextFileReader()
        # should raise a ValueError exception when no file path is set on the reader
        reader.read_data() 
        
def test_get_dataframe_without_other_cols(input_df):
    reader = TextFileReader()
    reader.data = input_df
    df_new = reader.get_dataframe('Articles')
    assert collections.Counter(df_new.columns) == collections.Counter(['TEXT'])
    
def test_get_dataframe_with_other_cols(input_df):
    reader = TextFileReader()
    reader.data = input_df
    df_new = reader.get_dataframe('Articles',other_columns=['Other_Col2'])
    assert collections.Counter(df_new.columns) == collections.Counter(['Other_Col2','TEXT'])
    
def test_verify_columns_exist_1(input_df):
    reader = TextFileReader()
    reader.data = input_df
    lst = reader.verify_columns_exist(['Other_Col1','Articles','Col_Not_Exists_In_Df'])
    assert collections.Counter(lst) == collections.Counter(['Col_Not_Exists_In_Df'])
    
def test_verify_columns_exist_2(input_df):
    reader = TextFileReader()
    reader.data = input_df
    lst = reader.verify_columns_exist(['Other_Col1','Articles'])
    assert len(lst) == 0
    
def test_is_text_column_yes(input_df):
    reader = TextFileReader()
    reader.data = input_df
    assert reader.is_text_column('Articles') == True
    
def test_is_text_column_no(input_df):
    reader = TextFileReader()
    reader.data = input_df
    assert reader.is_text_column('Other_Col2') == False

