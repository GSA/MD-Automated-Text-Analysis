import pandas as pd

class TextFileReader:
    
    def __init__(self, data_file_path):
        
        self.data = pd.read_excel(data_file_path)
        
        
    def to_dataframe(self) -> pd.DataFrame:

        df = self.data[['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS', \
                   'Please briefly describe an example of one burdensome administrative task or process which you believe is "low value"']]
        df.columns = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS','TEXT']
        full_df = df[df['TEXT'].isnull()==False]
        full_df = df[df['TEXT'].isna()==False]
        full_df = df[df['COMPONENT'].isna()==False]
        full_df = df[df['GRADELEVEL'].isna()==False]
        full_df.dropna(subset=['TEXT'],inplace=True)

        return full_df
    
    def to_dataframe2(self) -> pd.DataFrame:

        df = self.data[['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS', \
                   'Reason for filling position(s) with Federal Government Employee -OTHER']]
        df.columns = ['AGENCY','COMPONENT','SUB_COMPONENT','GRADELEVEL','SUP_STATUS','TEXT']
        full_df = df[df['TEXT'].isnull()==False]
        full_df = df[df['TEXT'].isna()==False]
        full_df = df[df['COMPONENT'].isna()==False]
        full_df = df[df['GRADELEVEL'].isna()==False]
        full_df.dropna(subset=['TEXT'],inplace=True)

        return full_df