import pandas as pd
import os

from textfilereader import TextFileReader
from topicsfinder import TopicsFinder

class TopicsAnalyser:
    
    scores = {
        'Department of Agriculture':{'scores':{'total':8,'manager':4,'nonmanager':8}},
        'Department of Commerce':{'scores':{'total':6,'manager':4,'nonmanager':6}},
        'Department of Defense':{'scores':{'total':10,'manager':16,'nonmanager':8}},
        'Department of Education':{'scores':{'total':6,'manager':14,'nonmanager':8}},
        'Department of Energy':{'scores':{'total':4,'manager':18,'nonmanager':6}},
        'Department of Health and Human Services':{'scores':{'total':6,'manager':10,'nonmanager':10}},
        'Department of Homeland Security':{'scores':{'total':6,'manager':6,'nonmanager':6}},
        'Department of Housing and Urban Development':{'scores':{'total':4,'manager':10,'nonmanager':4}},
        'Department of Justice':{'scores':{'total':8,'manager':12,'nonmanager':4}},
        'Department of Labor':{'scores':{'total':8,'manager':14,'nonmanager':6}},
        'Department of State':{'scores':{'total':14,'manager':6,'nonmanager':6}},
        'Department of the Interior':{'scores':{'total':10,'manager':14,'nonmanager':4}},
        'Department of the Treasury':{'scores':{'total':8,'manager':10,'nonmanager':8}},
        'Department of Transportation':{'scores':{'total':6,'manager':16,'nonmanager':6}},
        'Department of Veterans Affairs':{'scores':{'total':8,'manager':12,'nonmanager':6}},
        'Environmental Protection Agency':{'scores':{'total':14,'manager':12,'nonmanager':10}},
        'General Services Administration':{'scores':{'total':18,'manager':8,'nonmanager':6}},
        'National Aeronautics and Space Administration':{'scores':{'total':4,'manager':18,'nonmanager':6}},
        'National Science Foundation':{'scores':{'total':4,'manager':16,'nonmanager':12}},
        'Nuclear Regulatory Commission':{'scores':{'total':6,'manager':16,'nonmanager':6}},
        'Office of Personnel Management':{'scores':{'total':6,'manager':12,'nonmanager':6}},
        'Social Security Administration':{'scores':{'total':10,'manager':6,'nonmanager':6}},
        'Small Business Administration':{'scores':{'total':6,'manager':16,'nonmanager':6}},
        'U.S. Agency for International Development':{'scores':{'total':4,'manager':12,'nonmanager':8}}
        }
    
    def __init__(self, data_file_path: str, num_ngrams: int= 2, addl_stop_words: [str]= []):
        
        reader = TextFileReader(data_file_path)
        self.data = reader.to_dataframe()
        self.num_ngrams = num_ngrams
        self.addl_stop_words = addl_stop_words
        
        self._unique_comps = self.data['COMPONENT'].unique()
        self._unique_agenics = self.data['AGENCY'].unique()
        self._curr_dir = os.getcwd()
        
        
    def _show_export_message(self, filename: str):
        
        return print(f"Text topics were exported to {self._curr_dir}/{filename}")
    
    
    def get_topics_by_agency(self):
        topic_dict={}

        for agency in self._unique_agenics:
            data_filtered = self.data[self.data['AGENCY']==agency]
            topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
            num_topics = TopicsAnalyser.scores.get(agency).get('scores').get('total')        
            model, _ = topicsfinder.fit_LDA_model(num_topics)
            topic_dict[agency] = topicsfinder.get_topics(model)
        
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
        export_file = 'Agency_Topics.csv'
        agency_df.to_csv(export_file)
        
        self._show_export_message(export_file)
        

    def get_topics_by_agency_manager(self):
        topic_dict={}

        for agency in self._unique_agenics:
            data_filtered = self.data[(self.data['AGENCY']==agency) & (self.data['SUP_STATUS']==1)]
            topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
            num_topics = TopicsAnalyser.scores.get(agency).get('scores').get('manager')        
            model, _ = topicsfinder.fit_LDA_model(num_topics)
            topic_dict[agency] = topicsfinder.get_topics(model)
        
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
        export_file = 'Agency_Topics_Senior_Manager.csv'
        agency_df.to_csv(export_file)
        
        self._show_export_message(export_file)
        
        
    def get_topics_by_agency_nonmanager(self):
        topic_dict={}

        for agency in self._unique_agenics:
            data_filtered = self.data[(self.data['AGENCY']==agency) & (self.data['SUP_STATUS']==0)]
            topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
            num_topics = TopicsAnalyser.scores.get(agency).get('scores').get('nonmanager')        
            model, _ = topicsfinder.fit_LDA_model(num_topics)
            topic_dict[agency] = topicsfinder.get_topics(model)
        
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
        export_file = 'Agency_Topics_Non_Manager.csv'
        agency_df.to_csv(export_file)
        
        self._show_export_message(export_file)
        
        
    def get_topics_by_gradelevel(self):
        unique_grades = self.data['GRADELEVEL'].unique()
        topic_dict={}

        for grade in unique_grades:
            data_filtered = self.data[self.data['GRADELEVEL']==grade]
            topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
            num_topics = 10   # TODO: let the model find the best no. of topics     
            model, _ = topicsfinder.fit_LDA_model(num_topics)
            topic_dict[grade] = topicsfinder.get_topics(model)
        
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
        export_file = 'Grade_Topics.csv'
        agency_df.to_csv(export_file)
        
        self._show_export_message(export_file)


    def get_topics_by_agency_component_manager(self):
        topic_dict={}

        for agency in self._unique_agenics:
            unique_components = self.data[(self.data['AGENCY']==agency) & 
                                           (self.data['SUP_STATUS']==1)]['COMPONENT'].unique()
           
            temp_dict = {}

            for comps in unique_components:
#                 temp_dict[comps] = get_topics(self.data[(self.data['AGENCY']==agency) & (self.data['SUP_STATUS']==1)&(self.data['COMPONENT']==comps)])
    
#     unique_comps_topics_mang[agency] = temp_dict

                data_filtered = self.data[(self.data['AGENCY']==agency) & 
                                          (self.data['SUP_STATUS']==1) &
                                          (self.data['COMPONENT']==comps)]
                topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
                num_topics = 10 # TODO: figure out what number it should be        
                model, _ = topicsfinder.fit_LDA_model(num_topics)

                temp_dict[comps] = topicsfinder.get_topics(model)
                
            topic_dict[agency] = temp_dict
            
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict.items() ])).T
        export_file = 'Agency_Topics_Non_Manager.csv'
        agency_df.to_csv(export_file)
        
        self._show_export_message(export_file)


    
    