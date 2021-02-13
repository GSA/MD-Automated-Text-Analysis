import logging, re, ntpath
from topicsfinder import TopicsFinder
import optuna
import numpy as np
import pandas as pd

class TopicsFinderTuner:
    
    def __init__(self, data: pd.DataFrame, num_ngrams: int= 2, addl_stop_words: [str]= []):
        self.data = data
        self.num_ngrams = num_ngrams
        self.addl_stop_words = addl_stop_words
        
        
    def objective(self, trial):
        # set up the search sapce of the hyperparameters 
        k = trial.suggest_int('num_topics', 1, 10)
        a = trial.suggest_categorical('alpha', list(np.arange(0.01, 1, 0.3)) + ['symmetric','asymmetric'])
        b = trial.suggest_categorical('eta', list(np.arange(0.01, 1, 0.3)) + ['symmetric'])
        chunksize = trial.suggest_int('chunksize', 100, 2000, step=100)
        passes = trial.suggest_int('passes', 1, 10, step=2)
        iterations = trial.suggest_int('iterations', 50, 500, step=50)

        self.model = TopicsFinder(self.data, self.num_ngrams, self.addl_stop_words)
        _, cv = self.model.fit_LDA_model(
            random_state=100,
            eval_every=None,
            chunksize=chunksize,
            passes=passes,
            iterations=iterations,
            num_topics = k,
            alpha = a,
            eta = b,
        )
        score = cv.get_coherence() 
        trial.report(score, 0)
        # Handle pruning based on the intermediate value.
        if trial.should_prune():
            raise optuna.exceptions.TrialPruned()
        return score
        
        # x = trial.suggest_float("x", -10, 10)
        # return (x - 2) ** 2
    

    def tune(self):
        optuna.logging.get_logger("optuna").addHandler(logging.handlers.RotatingFileHandler("optuna.log",maxBytes=100000,backupCount=3))
        # stop the study when there are 3 consecutive prunes
        threshold = 3
        study_stop_cb = StopWhenTrialKeepBeingPrunedCallback(threshold)
        # # save the current study in database so that it can be used as the starting point for later subsequent trails if load_if_exists is set to True on optuna.create_study()
        study_name = "topicsfinder_tuning-study"   # TODO: use a unique name for different datasets
        # storage_name = f"sqlite:///{study_name}.db"

        # create a study object and optimize the objective function.
        # study = optuna.create_study(direction='maximize', study_name=study_name, storage=storage_name, load_if_exists=True)
        study = optuna.create_study(direction='maximize', study_name=study_name)
        study.optimize(self.objective, n_trials=100, callbacks=[study_stop_cb])
        # return the best hyperparameters and coherence score
        return (study.best_params, study.best_value)


class StopWhenTrialKeepBeingPrunedCallback:
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
    
    