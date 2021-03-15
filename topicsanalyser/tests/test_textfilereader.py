import pytest
from ..textfilereader import TextFileReader

def test_init():
    file = '/usr/someone/myfile.csv'
    reader = TextFileReader(file)
    assert reader.data_file_path == file    