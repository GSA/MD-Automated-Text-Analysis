import pandas as pd
import os

from textfilereader import TextFileReader
from topicsfinder import TopicsFinder
from topicsfinder_tuner import TopicsFinderTuner

class TopicsAnalyser:
    
    def __init__(self, data: pd.DataFrame, output_filename: str = 'Topics'): 
        self.data = data
        self.output_filename = output_filename
                      
    def _get_topics_by_group(self, data: pd.DataFrame, num_topics: int, groupby_cols: list, num_ngrams: int, addl_stop_words: list):
        # check if there is grouping specified for this dataset
        if (len(groupby_cols) == 0):
            tuner = TopicsFinderTuner(data, num_topics, num_ngrams, addl_stop_words)
            try:
                best_trial = tuner.tune()
            except ValueError:
                return 'no data'

            # get the no. of topics from the best parameters
            best_num_topics = best_trial['trial'].params['num_topics']
            # return the topics for the group
            return best_trial['model'].show_topics(num_topics = best_num_topics)

        # handle the lower level of grouping
        col_name = groupby_cols[0]
        # get all the group names of next level
        col_unique_values = data[col_name].unique()
        topic_dict = {}
        for group in col_unique_values:
            # get the data of current group
            group_data = data[data[col_name] == group]
            # recursively call this function to process the data of next level grouping
            topic_dict[group] = self._get_topics_by_group(group_data, num_topics, groupby_cols[1:], num_ngrams, addl_stop_words)
            
        return topic_dict
    
    
    def _flatten_dictionary(self, topics, row_values: list = []):
        if (isinstance(topics, dict) == False):
            # return a row of the current group
            return [row_values + [pd.Series(topics)]]

        results = []
        # return a list of rows for the current group
        for k, v in topics.items():
            # further flatten the sub-dictionaries
            results = results + self._flatten_dictionary(v, row_values + [k])

        return results
        

    def get_topics(self, num_topics: int, groupby_cols: list = [], num_ngrams: int= 2, addl_stop_words = []):
        # TODO: handle exceptions and return error message
        topics = self._get_topics_by_group(self.data, num_topics, groupby_cols, num_ngrams, addl_stop_words)                   
        df = pd.DataFrame(self._flatten_dictionary(topics), columns= groupby_cols + ['Topics'])
        col_list = ['Topics'] + groupby_cols + [f"Topic {i}" for i in range(num_topics)]
        df = df.reindex(columns = col_list)
        
        for i in range(len(df)):
            for t in range(num_topics):
                try:
                    df[f"Topic {t}"].iloc[i] = df['Topics'].iloc[i][t][1]
                except KeyError:
                    pass

        export_file = f'{self.output_filename}.csv'
        # exclude the 'Topics' column from export
        df.iloc[:, 1:].to_csv(export_file)

        return f"Output file: {os.getcwd()}/{export_file}"



    
    