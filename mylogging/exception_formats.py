import sys
import traceback   

def system_hook_format(type, value, tb) -> str:
    """
    Intended to be assigned to sys.exception as a hook.
    Gives programmer opportunity to do something useful with info from uncaught exceptions.

    Parameters
    type: Exception type
    value: Exception's value
    tb: Exception's traceback
    """

    # NOTE: because format() is returning a list of string,
    # I'm going to join them into a single string, separating each with a new line
    traceback_details = '\n'.join(traceback.extract_tb(tb).format())

    error_msg = "Uncaught exception -\n" \
                f"Type: {type}\n" \
                f"Value: {value}\n" \
                f"Traceback: {traceback_details}"
    
    return error_msg
