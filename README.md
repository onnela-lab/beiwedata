# Introduction
`beiwe-desktop` is a set of Python scripts designed to help munge, analyze, and manipulate data generated by the Beiwe application. 

# Table of Contents
- [Usage](#usage)
- [Data overview](#data-overview)

# Usage
`from beiwe-desktop import *` is the standard way to import and this document will assume `beiwe-desktop` has been imported to the top level. If you `import as`, please adjust the usage examples accordingly.

# Data overview
There are a total of 12 types of files generated by the `beiwe` app. Files are stored as comma-separated values (`csv`) files and **every** file contains column headers (including empty files). Empty files are created when the application is activated and data is being collected, but there is no data to collect. For example, during a "WiFi" check the application will activate, check for WiFi signals, and record them. During this time, it may also check to see if there is any new Bluetooth or call/text information to gather. If no new information exists, it will create the file with the headers, but no other rows.

\#|Data stream|File prefix|\# Col
:-:|-----------|-----------|:---:
1|Accelerometer|`accel`|5
2|Bluetooth|`bluetoothLog`|3
3|Phone calls|`callLog`|4
4|GPS|`gps`|5
5|IDs|`identifiers`|4
6|Beiwe logs|`logFile`|1
7|Power State|`powerState`|2
8|Survey (1)|`surveyAnswers`|5
9|Survey (2)|`surveyTimings`|6
10|Text messages|`textsLog`|5
11|Voice memos|`voiceRecording`|NA
12|WiFi|`wifiLog`|3

## Timestamps
Each file prefix above is followed by `_[timestamp].csv`. The timestamp is Java time in UTC, which is microseconds from epoch, and represents the *time of file creation*. Thus, note that this timestamp may differ from the timestamp you see online which represents the time of file upload.[^fn-file_upload]

In order to use most conversion tools (which are designed for [Unix time](https://en.wikipedia.org/wiki/Unix_time)), simply perform integer division by 1000. For example, in `Python`, one must first perform `int(timestamp / 1000)` before using the `datetime` module to convert to human-readable time. In `Microsoft Excel` one might use a formula such as `=((timestamp/1000) / 86400) + 25569` and then convert the cell to datetime.

See [EpochConverter](http://www.epochconverter.com/) for more ways to manipulate Unix time into various programming languages.

## Accelerometer data
Accelerometer files contain 5 columns: `timestamp`, `accuracy`, `x`, `y`, and `z`.[^fn-accel_note]

## Bluetooth


## Phone calls
## GPS
## IDs
## Beiwe logs
## Power State
## Survey Answers
## Survey Timings
## Text messages
## Voice memos
## WiFi

# Functions
More information about each function can be found in the function's docstring (i.e., `help([function])` or `?[function]`). This is just a list of functions to give you an idea of what has already been done.

# Footnotes
[^fn-file_upload]: The app is designed to only upload when there is sufficient battery (or it is plugged in) and it is connected to WiFi.
[^fn-accel_note]: **NOTE:** It is an open question about the bounds of the `x`, `y`, and `z`. In all our test data, the bounds are [-20, 20]; however, this may be specific to each handset and/or version of Android.