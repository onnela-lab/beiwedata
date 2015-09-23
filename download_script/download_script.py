print ""
try:
    import os
    import boto
    from boto import connect_s3
    from boto.exception import S3ResponseError
    from Crypto.Cipher import AES # library name to install: pycrypto
except ImportError as import_e:
    missing_dependencies_error = """Uh-oh, you have some missing dependencies.
    Open up the download script and and check the dependencies near the top,
    before this error message, and ensure that you have them all.  We strongly
    recommend using PIP, the Python package manager, to install these.
    Directions for installing pip can be found at https://pip.pypa.io/en/stable/installing/
\n\n"""
    print missing_dependencies_error
    raise import_e

################################################################################

try:
    from download_script_credentials import (AWS_ACCESS_KEY_ID as _AWS_ACCESS_KEY_ID,
                                             AWS_SECRET_ACCESS_KEY as _AWS_SECRET_ACCESS_KEY,
                                             STUDY_ID as _STUDY_ID,
                                             STUDY_KEY as _STUDY_KEY,
                                             S3_BUCKET_NAME as _S3_BUCKET_NAME)
except ImportError as e:
    print """Uh-oh, something went wrong in trying to import your access credentials.
Ensure that you have a file named download_script_credentials located in the same
folder as the download script, and that it contains the following variables:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    STUDY_ID
    STUDY_KEY
    S3_BUCKET_NAME\n\n"""
    raise e

if not _AWS_ACCESS_KEY_ID or not _AWS_SECRET_ACCESS_KEY:
    print "Please edit download_script_credentials.py to contain AWS credentials."
    raise ImportError("you have empty AWS credentials")

if not _STUDY_ID:
    _STUDY_ID = raw_input("Enter the study ID you will be downloading from:\n")
if not _STUDY_KEY:
    _STUDY_KEY = raw_input("Enter the decryption key for this study:\n")

_CONN = connect_s3(aws_access_key_id=_AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=_AWS_SECRET_ACCESS_KEY)

try:
    _bucket = _CONN.get_bucket(_S3_BUCKET_NAME, validate=True)
except S3ResponseError:
    print """Unable to connect to the S3 bucket.  Please check that your credentials
and bucket name are all correct and valid and try again.  If the problem persists
contact the study administrator.\n\n"""
    exit()

################################################################################

def _get_user_folder_path(patient_id):
    return 

def _sanitize_file_name(name):
    #TODO: this doc may be inaccurate
    """ Pulls out the unenecessary prefix data (study id and user id) and leaves
    he useful file info.  Also converts slashes to underscores for os compatibility. """
    return name.split('/', 1)[-1].replace("/", "_")

def _decrypt_file(input_string):
    """ Decrypts Beiwe user data. """
    iv = input_string[:16]
    return AES.new( _STUDY_KEY, AES.MODE_CFB, segment_size=8, IV=iv ).decrypt( input_string[16:] )

def _download(data_type, patient_id):
    folder_path = patient_id + '/'
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    extant_files = os.listdir(folder_path)
    
    prefix = _STUDY_ID + '/' + patient_id + '/' + data_type
    download_list = _bucket.list(prefix=prefix)
    
    for s3_key in download_list:
        local_file_name = _sanitize_file_name(s3_key.name)
        #print statement of current status... ugly.
        if local_file_name in extant_files:
            print local_file_name, "... file already exists, skipping"
            continue
        print "downloading", local_file_name
        with open(patient_id + '/' + local_file_name, 'w+') as f:
            f.write( _decrypt_file(s3_key.read()) )

def download_all(patient_id):
    _download("", patient_id)

def download_bluetooth(patient_id):
    _download("bluetooth", patient_id)

def download_wifi(patient_id):
    _download("wifi", patient_id)

def download_debug(patient_id):
    _download("logFile", patient_id)

def download_accel(patient_id):
    _download("accel", patient_id)

def download_gps(patient_id):
    _download("gps", patient_id)

def download_audio(patient_id):
    _download("voiceRecording", patient_id)

def download_texts(patient_id):
    _download("texts", patient_id)

def download_calls(patient_id):
    _download("call", patient_id)

def download_power_state_timings_data(patient_id):
    _download("powerState/", patient_id)

def download_daily_survey_results_data(patient_id):
    _download("surveyAnswers/Daily", patient_id)

def download_weekly_survey_results_data(patient_id):
    _download("surveyAnswers/Weekly", patient_id)

def download_weekliy_survey_timings_data(patient_id):
    _download("surveyTimings/Weekly", patient_id)

def download_daily_survey_timings_data(patient_id):
    _download("surveytimings/Weekly", patient_id)

users = [x for x in _bucket.list(prefix= _STUDY_ID + '/', delimiter='/') if isinstance(x, boto.s3.key.Key) ]
users = [str(x.name.rsplit('/')[-1]) for x in users]
study_id = _STUDY_ID
print """ a variable "users" has been created, it contains a list of all the
participants of the study.  In addition the following functions are available to
you:

download_all( "patient_id" )
download_debug( "patient_id" )
download_bluetooth( "patient_id" )
download_wifi( "patient_id" )
download_accel( "patient_id" )
download_gps( "patient_id" )
download_audio( "patient_id" )
download_texts( "patient_id" )
download_calls( "patient_id" )
download_power_state_timings_data( "patient_id" )
download_daily_survey_results_data( "patient_id" )
download_weekly_survey_results_data( "patient_id" )
download_weekliy_survey_timings_data( "patient_id" )
download_daily_survey_timings_data( "patient_id" )

When you download files it will do so into to a folder in the current directory,
the name of that folder is the ID of the supplied user.

If you are using iPython (strongly recommended) you can use the special functions
"cd" and "pwd" as you would in a regular bash terminal to navigate your file system.

Start by typing out "users" to view the user list, or "study_id" to check which 
study you are configured for.
""" 

