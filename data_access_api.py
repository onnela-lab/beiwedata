# API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
# slightly more human notation: YYYY-MM-DDThh:mm:ss
# (that is the letter T between date and time)
# 1990-01-31T07:30:04 gets you jan 31 1990 at 7:30:04am

import urllib, urllib2, StringIO, zipfile, json
from datetime import datetime
from os import path
from my_data_access_api_credentials import ACCESS_KEY, SECRET_KEY

API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ACCELEROMETER = "accelerometer"
BLUETOOTH = "bluetooth"
CALL_LOG = "calls"
GPS = "gps"
IDENTIFIERS = "identifiers"
LOG_FILE = "app_log"
POWER_STATE = "power_state"
SURVEY_ANSWERS = "survey_answers"
SURVEY_TIMINGS = "survey_timings"
TEXTS_LOG = "texts"
VOICE_RECORDING = "audio_recordings"
WIFI = "wifi"

def make_request(study_id, access_key=ACCESS_KEY, secret_key=SECRET_KEY, user_ids=None, data_streams=None, time_start=None, time_end=None):

     url = 'https://studies.beiwe.org/get-data/v1'
     values = {'access_key' : access_key,
               'secret_key' : secret_key,
               'study_id' : study_id }

     if user_ids: values['user_ids'] = user_ids
     if data_streams: values['data_streams'] = data_streams

     # Uncomment the below lines to enable (time zone unaware) datetime support
     if time_start:
          # if isinstance(time_start, datetime):
               # time_start = time_start.strftime(API_TIME_FORMAT)
          values['time_start'] = time_start
     if time_end:
          # if isinstance(time_end, datetime):
               # time_end = time_end.strftime(API_TIME_FORMAT)
          values['time_end'] = time_end

     if path.exists("master_registry"):
          with open("master_registry") as f:
               old_registry = json.load(f)
               f.close()
               values["registry"] = json.dumps(old_registry)
     else: old_registry = {}

     print "sending request, this could take some time."

     req = urllib2.Request(url, urllib.urlencode(values))
     response = urllib2.urlopen(req)
     return_data = response.read()

     print "Data received.  Unpacking and overwriting any updated files into", path.abspath('.')

     z = zipfile.ZipFile(StringIO.StringIO(return_data))
     z.extractall()

     with open("registry") as f:
          new_registry = json.load(f)
          f.close()

     old_registry.update(new_registry)
     with open("master_registry", "w") as f:
          json.dump(old_registry, f)
     path.os.remove("registry")
     print "Operations complete."
     #Uncomment the following line to have the function return a list of newly updated files.
     # return [name.filename for name in z.filelist if name.filename != "registry"]
