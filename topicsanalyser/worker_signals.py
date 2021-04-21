from PyQt5.QtCore import QObject, pyqtSignal

# Custom signals can only be defined on objects derived from QObject. 
# Since QRunnable is not derived from QObject we can't define the signals there directly. 
# A custom QObject to hold the signals is the simplest solution.
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
        
    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        object indicating % progress

    '''    
    
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)
    