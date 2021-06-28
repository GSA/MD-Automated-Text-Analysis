import pandas as pd
import os
from topicsfinder_tuner import TopicsFinderTuner

class TopicsAnalyser:
    
    def __init__(self, data: pd.DataFrame, output_filename: str = 'Topics', **kwargs): 
        self.data = data
        self.output_filename = output_filename
        # optional parameters, such as the ones for model tuning
        self.kwargs = kwargs 
        
                      
    def _get_topics_by_group(self, data: pd.DataFrame, num_topics: int, groupby_cols: list, num_ngrams: int, addl_stop_words: list, **kwargs) -> dict:
        # check if there is grouping specified for this dataset
        if (len(groupby_cols) == 0):
            tuner = TopicsFinderTuner(data, num_topics, num_ngrams, addl_stop_words, **kwargs)
            try:
                best_trial = tuner.tune()
            except ValueError:
                # return a dummy topic, [(topic_num, topic_content)] and a score of 'None for this group
                return [(0,'no data')], None

            # get the no. of topics from the best parameters
            best_num_topics = best_trial['trial'].params['num_topics']
            # return the topics and its coherence score for the group
            return best_trial['model'].show_topics(num_topics = best_num_topics), best_trial['score']

        # get the first column name from the groupby columns, e.g. "AGENCY" from ["AGENCY","COMPONENT",...]
        col_name = groupby_cols[0]
        # get all the unique groups from the column 
        col_unique_values = data[col_name].unique()
        topic_dict = {}
        studyname = kwargs['studyname']
        for group in col_unique_values:
            # get the data of current group
            group_data = data[data[col_name] == group]
            # create a new Optuna study name for the current group
            kwargs['studyname'] = f"{studyname} -> {group}"
            # recursively call this function to process the data of next level grouping (note: groupby_cols[1:] = ["COMPONENT",...] here as an example)
            topic_dict[group] = self._get_topics_by_group(group_data, num_topics, groupby_cols[1:], num_ngrams, addl_stop_words, **kwargs)
            
        return topic_dict
    
    
    def _flatten_dictionary(self, topic_dict, row_values: list = []) -> list:
        if (isinstance(topic_dict, dict) == False):
            # return a row of the current group (topics_dict[0] = topics, topics_dict[1] = score)
            return [row_values + [pd.Series(topic_dict[0])] + [topic_dict[1]]]

        results = []
        # return a list of rows for the current group
        for k, v in topic_dict.items():
            # further flatten the sub-dictionaries
            results = results + self._flatten_dictionary(v, row_values + [k])

        return results
        

    def get_topics(self, num_topics: int, groupby_cols: list = [], num_ngrams: int= 2, addl_stop_words = []) -> str:
        TopicsFinderTuner.configure_logger()
        topics = self._get_topics_by_group(self.data, num_topics, groupby_cols, num_ngrams, addl_stop_words, **self.kwargs)
        df = pd.DataFrame(self._flatten_dictionary(topics), columns= groupby_cols + ['Topics','Coherence Score'])        
        col_list = ['Topics'] + groupby_cols + [f"Topic {i+1}" for i in range(num_topics)] + ['Coherence Score']
        df = df.reindex(columns = col_list)
        
        for i in range(len(df)):
            for t in range(num_topics):
                try:
                    df[f"Topic {t+1}"].iloc[i] = df['Topics'].iloc[i][t][1]
                except KeyError:
                    pass

        export_file = f'{self.output_filename}.csv'
        # exclude the 'Topics' column from export
        df.iloc[:, 1:].to_csv(export_file)

        return f"Output file: {os.getcwd()}/{export_file}"


    
    