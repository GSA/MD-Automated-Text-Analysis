import logging, re, ntpath
from topicsfinder import TopicsFinder
import optuna
import numpy as np
import pandas as pd
import pickle
import os

class TopicsFinderTuner:
    
    def __init__(self, data: pd.DataFrame, studyname: str= None, max_num_topics: int= 10, num_ngrams: int= 2, addl_stop_words: [str]= []):
        self.data = data
        self.max_num_topics = max_num_topics
        self.num_ngrams = num_ngrams
        self.addl_stop_words = addl_stop_words
        self.studyname = studyname
        
        
    def objective(self, trial: optuna.Trial) -> float:
        # set up the search space of the hyperparameters 
        k = trial.suggest_int('num_topics', 1, self.max_num_topics)
        a = trial.suggest_categorical('alpha', list(np.arange(0.01, 1, 0.3)) + ['symmetric','asymmetric'])
        b = trial.suggest_categorical('eta', list(np.arange(0.01, 1, 0.3)) + ['symmetric'])
        chunksize = trial.suggest_int('chunksize', 100, 2000, step=100)
        passes = trial.suggest_int('passes', 1, 10, step=2)
        iterations = trial.suggest_int('iterations', 50, 500, step=50)

        # train the model using the hyperparamters suggested by Optuna
        finder = TopicsFinder(self.data, self.num_ngrams, self.addl_stop_words)
        model, cv = finder.fit_model(
            random_state=100,
            eval_every=None,
            chunksize=chunksize,
            passes=passes,
            iterations=iterations,
            num_topics = k,
            alpha = a,
            eta = b
        )
        score = cv.get_coherence()
        # report an objective function value for a given step. The reported values are used by the pruners to determine whether this trial should be pruned. 
        trial.report(score, 0)
        # handle pruning based on the intermediate value.
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()

        # save a trial info object to a file.
        trial_info = {'trial': trial, 'model': model}
        with open(f'{trial.number}.pickle', 'wb') as fout:
            pickle.dump(trial_info, fout)
        
        return score
            

    def tune(self):
        # stop the study if the model is being pruned 3 times in a row that indicates the current hyperparameters are closed to the optimal ones
        threshold = 3
        study_stop_cb = StopWhenTrialKeepBeingPrunedCallback(threshold)

        # create a study object and optimize the objective function.
        study = optuna.create_study(direction='maximize', study_name= self.studyname)
        study.optimize(self.objective, n_trials=100, callbacks=[study_stop_cb])
        
        # Load the best trial info object from file.
        with open(f'{study.best_trial.number}.pickle', 'rb') as fin:
            best_trial = pickle.load(fin)
            
        # remove the temporary pickle files
        self._remove_pickles()

        return best_trial


    @classmethod
    def configure_logger(cls) -> None:
        """
        Configure file handler for Optuna logging
        """
        logger = optuna.logging.get_logger("optuna")
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        handler = logging.handlers.RotatingFileHandler("optuna.log",maxBytes=5000000,backupCount=3)
        handler.setFormatter(formatter)        
        logger.addHandler(handler)
       
        
    def _remove_pickles(self):
        dir_name = os.getcwd()
        files = os.listdir(dir_name)

        for file in files:
            if file.endswith(".pickle"):
                os.remove(os.path.join(dir_name, file))
                

class StopWhenTrialKeepBeingPrunedCallback:
    '''
    A utility class used as a callback in the study.optimize() function for tuning early stopping
    '''
    def __init__(self, threshold: int):
        self.threshold = threshold
        self._consequtive_pruned_count = 0

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:
        if trial.state == optuna.trial.TrialState.PRUNED:
            self._consequtive_pruned_count += 1
        else:
            self._consequtive_pruned_count = 0

        if self._consequtive_pruned_count >= self.threshold:
            study.stop()    
    
    