import pandas as pd

class TextFileReader:
 
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self.data = None
        
    def read_data(self):
        self.data = pd.read_excel(self.data_file_path)

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
        is_text_col = True
        # make sure the column exists before checking its type
        if text_col_name in self.data.columns:
            is_text_col = self.data[text_col_name].apply(type).eq(str).any()
            
        return is_text_col
        