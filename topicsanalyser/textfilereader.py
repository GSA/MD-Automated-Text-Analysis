import pandas as pd
import os

class TextFileReader:
    """
    A class used to read text files, create a Panda DataFrames and verify if the columns
    in the dataframe meet the requirements for text mining.
    """
 
    def __init__(self, data_file_path: str = None):
        self.data_file_path = data_file_path
        self.data = None
        self.filesize = None
        
    def read_data(self):
        """
        data file is not read when the class is instantiated for various application
        scenarios. So this method must be explictly called to read data in.
        
        Raises:
            ValueError: raise when data path is not specified
        """
        if ((self.data_file_path is None) or (len(self.data_file_path.strip()) == 0)):
            raise ValueError('data path is missing.')
        
        self.data = pd.read_excel(self.data_file_path)
        self.filesize = os.path.getsize(self.data_file_path)

    def get_dataframe(self, text_column: str, other_columns: list = []) -> pd.DataFrame:
        if (self.data is None):
            self.read_data()

        cols = other_columns + [text_column]
        df = self.data[cols]
        # rename the original text column in dataframe to 'TEXT'
        df.columns = other_columns + ['TEXT']
        df.dropna(subset=['TEXT'],inplace=True)
        return df
   
    def verify_columns_exist(self, columns: list ) -> list:
        if (self.data is None):
            self.read_data()

        cols_not_exist = []
        for col in columns:
            if col not in self.data.columns:
                cols_not_exist.append(col + ', ')
                
        return cols_not_exist
    
    def is_text_column(self, text_col_name: str) -> bool:
        if (self.data is None):
            self.read_data()

        is_text_col = True
        # make sure the column exists before checking its type
        if text_col_name in self.data.columns:
            is_text_col = self.data[text_col_name].apply(type).eq(str).any()
            
        return is_text_col
        