import pandas as pd
import os

from textfilereader import TextFileReader
from topicsfinder import TopicsFinder

class TopicsAnalyser:
    
    def __init__(self, data_file_path: str): 
        reader = TextFileReader(data_file_path)
        self.data = reader.to_dataframe()
        
                    
    def _get_topics_by_group(self, data: pd.DataFrame, num_topics: int, groupby_cols: list, num_ngrams: int, addl_stop_words: list):
        
        if (len(groupby_cols) == 0):
            topicsfinder = TopicsFinder(data, num_ngrams, addl_stop_words)
            try:
                model, _ = topicsfinder.fit_LDA_model(num_topics)
            except ValueError:
                return 'no data'

            return topicsfinder.get_topics(model)

        col_name = groupby_cols[0]
        col_unique_values = data[col_name].unique()
        topic_dict = {}
        for group in col_unique_values:
            group_data = data[data[col_name] == group]
            topic_dict[group] = self._get_topics_by_group(group_data, num_topics, groupby_cols[1:], num_ngrams, addl_stop_words)
            
        return topic_dict
                    

    def get_topics(self, num_topics: int, groupby_cols = [], num_ngrams: int= 2, addl_stop_words = []):

        topics = self._get_topics_by_group(self.data, num_topics, groupby_cols, num_ngrams, addl_stop_words)
        
        return topics
    
#         if (isinstance(topics, dict)):
#             agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
#         else
#         export_file = 'Agency_Topics_Non_Manager.csv'
#         agency_df.to_csv(export_file)
        
#         self._show_export_message(export_file)


    
    