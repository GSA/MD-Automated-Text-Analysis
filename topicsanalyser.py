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
        
        
    def export_topics_by_agency(self):
        topic_dict_agency={}

        for agency in self._unique_agenics:
            data_filtered = self.data[self.data['AGENCY']==agency]
            topicsfinder = TopicsFinder(data_filtered, self.num_ngrams, self.addl_stop_words)
            num_topics = TopicsAnalyser.scores.get(agency).get('scores').get('total')        
            model, _ = topicsfinder.fit_LDA_model(num_topics)
            topic_dict_agency[agency] = topicsfinder.get_topics(model)
        
        export_file = 'Agency_Topics.csv'
        agency_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in topic_dict_agency.items() ])).T
        agency_df.to_csv(export_file)
        
        print(f"Text topics were exported to {self._curr_dir}/{export_file}")

    
    