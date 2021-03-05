# these are the commands to install the required packages
python3 -m pip install -r requirements.txt --user --no-warn-script-location --use-feature=2020-resolver
python3 -m spacy download en_core_web_sm --user

# command to run the application
python3 topicsanalyser_ui_app_v2.py