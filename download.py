import urllib
import urllib2
import StringIO
import zipfile
import json
import os
import errno
from datetime import datetime


## Convenience variables
ACCEL = "accelerometer"
BT = "bluetooth"
CALL_LOG = "calls"
GPS = "gps"
IDS = "identifiers"
LOGS = "app_log"
POWER = "power_state"
SURVEY_ANSWERS = "survey_answers"
SURVEY_TIMINGS = "survey_timings"
TEXTS = "texts"
VOICE = "audio_recordings"
WIFI = "wifi"

## Helper functions
def mkdir_p(path):
    """Same as `mkdir -p` in linux -- makes directory with intermediates 
    
    Notes
    -----
    Should handle most race conditions. If directory exists, silently passes.
    
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


class cd:
    """Class for running code in a different directory
    
    Notes
    -----
    Use with a context manager. Will automatically move back to original
    working directory once context manager is closed.
    
    Usage
    -----
    ```
    # Code in current working directory here
    
    with cd("../other_non_working_directory"):
        # Code for new working directory here
        
    # Back to original working directory here
    
    Example
    -------
    # To download beiwe data to a specified folder called `../data/`
    from beiwedata import *
    mkdir_p('../data/')   # make the folder
    
    with cd('../data/'):
        make_request(ENTER_INFO_HERE)    
    ```
    
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def make_request(study_id, access_key, secret_key, user_ids=None, 
                 data_streams=None, time_start=None, time_end=None, 
                 folder='.', return_new=False, verbose=True):
    """Submit a download request to the studies.beiwe.org server
     
    Parameters
    ----------
    study_id : a string containing the ID of a study (see: Details)
    access_key : a string containing researcher-specific API access key
    secret_key : a string containing reseracher-specific API secret key
    user_ids : a list of strings with user IDs for a specific study
    data_streams : list of data streams (see: Details)
    time_start : YYYY-MM-DDThh:mm:ss (note capital T -- see: Details)
    time_end : YYYY-MM-DDThh:mm:ss (note capital T -- see: Details)
    folder : download to this folder (default is current working directory)
    return_new : if True, return a list of new/updated files
    verbose : if True, provide feedback
    
    Notes
    -----
    It is preferrable to download all the data in the same directory so the
    function can leverage the `registry` file and prevent downloading 
    redundant data and speeding up the process.
     
    Details
    -------
    - study_id (sample study: '56cf16231206f7536acbaf58') : required for any 
        query. Currently the only way to view the ID of a given study on
        studies.beiwe.org website is to look at the url while viewing a study's
        main page. An API function is under development.
        
    - access_key / secret_key : you can save your credentials in the 
        `download_creds.py` file and use `access_key=ACCESS_KEY`. See the
        studies.beiwe.org website to reset your credentials (Manage Credentials)
    
    - user_ids : a list of strings. For example, we can specify the two sample 
        users as `['axos62v5', 'f8jioba2']`. If no user is specified, ALL users 
        are downloaded. 
    
    - data_streams : a list of strings. For convenience, we have defined the 
        valid strings below. Thus, `[ACCEL, BT]` is equivalent to using 
        `['accelerometer', 'bluetooth']`. If no stream is specified, ALL 
        available streams are downloaded. 
        - ACCEL = "accelerometer"
        - BT = "bluetooth"
        - CALL = "calls"
        - GPS = "gps"
        - IDS = "identifiers"
        - LOGS = "app_log"
        - POWER = "power_state"
        - SURVEY_ANSWERS = "survey_answers"
        - SURVEY_TIMINGS = "survey_timings"
        - TEXTS = "texts"
        - VOICE = "audio_recordings"
        - WIFI = "wifi"
    - time_start / time_end : string format should be YYYY-MM-DDThh:mm:ss noting
        the "T" separating date and time. Example: 1990-01-31T07:30:04 gets you 
        Jan 31 1990 at 7:30:04 AM. Times are inclusive (you will receive data
        contained in files that match the times exactly). Missing times imply
        all data in that direction (e.g., missing time_start implies 
        downloading from first available data and missing time_end implies 
        downloading to the most current data).
        
    """
    if folder != '.':
        mkdir_p(folder)
    
    with cd(folder):    
        url = 'https://studies.beiwe.org/get-data/v1'
        values = {'access_key' : access_key,
                    'secret_key' : secret_key,
                    'study_id' : study_id }
        API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

        if user_ids: values['user_ids'] = json.dumps(user_ids)
        if data_streams: values['data_streams'] = json.dumps(data_streams)
    
        if time_start:
            if isinstance(time_start, datetime): 
                time_start = time_start.strftime(API_TIME_FORMAT)
            values['time_start'] = time_start
    
        if time_end:
            if isinstance(time_end, datetime):
                time_end = time_end.strftime(API_TIME_FORMAT)
            values['time_end'] = time_end

        if os.path.exists("master_registry"):
            with open("master_registry") as f:
                old_registry = json.load(f)
                values["registry"] = json.dumps(old_registry)
        else: old_registry = {}

        if verbose:
            print "Sending request, this could take some time."

        req = urllib2.Request(url, urllib.urlencode(values))
        response = urllib2.urlopen(req)
        return_data = response.read()
        
        z = zipfile.ZipFile(StringIO.StringIO(return_data))
        z.extractall()  
        # could use z.extractall(path=...) but cd() makes registry mgmt easier
        
        if verbose:
            print "Data received."
            print "Unpacking files:", os.path.abspath('.')

        with open("registry") as f:
            new_registry = json.load(f)

        old_registry.update(new_registry)
        with open("master_registry", "w") as f:
            json.dump(old_registry, f)
        os.path.os.remove("registry")
        
        new_files = [name.filename for name in z.filelist 
                        if name.filename != "registry"]
        
        if verbose:
            print "Completed: " + str(len(new_files)) + " new files"
     
        if return_new:
            return new_files

## Wrapper functions start here
def download_accel(study_id, access_key, secret_key, user_ids=None, 
            time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only accelerometer data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["accelerometer"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_audio(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only audio data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["audio_recordings"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_bt(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only Bluetooth data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["bluetooth"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_calls(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only call log data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["calls"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_gps(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only GPS data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["gps"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_ids(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only user identifer data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["identifiers"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_logs(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only application log data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["app_log"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_power(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only power state data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["power_state"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_surveyA(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only survey answer data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["survey_answers"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_surveyT(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only survey timing data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["survey_timings"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_texts(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only text log data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["texts"], 
                    time_start=time_start, time_end=time_end, folder=folder)


def download_wifi(study_id, access_key, secret_key, user_ids=None, 
                    time_start=None, time_end=None, folder='.'): 
    """ Wrapper function to download only survey answer data 
    
    Notes
    -----
    See `help(make_request)` for more documentation.
    """
    
    make_request(study_id=study_id, access_key=access_key, user_ids=user_ids, 
                    secret_key=secret_key, data_streams=["wifi"], 
                    time_start=time_start, time_end=time_end, folder=folder)
























