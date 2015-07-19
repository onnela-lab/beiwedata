# -*- coding: utf-8 -*-
"""M Kiang's helper functions for Beiwe data analysis.

    Based some of this on the Zagaran csv_tools.py helper file, but much of it
    was rewritten so I could figure out what was going on and docstrings were
    added so others could figure out what was going on.

    PEP8
    ----
    Some of the initial function lines are too long. Code collapsing doesn't
    work in TextMate unless the first line of a function is unbroken. Thus,
    this does not adhere to PEP8.
"""

import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import datetime
import csv
# import pytz
# import shapefile
# import fiona
# from pytz import timezone
from matplotlib.dates import HourLocator
from scipy.io import wavfile
from mpl_toolkits.basemap import Basemap

# # Plot settings
pd.set_option('display.mpl_style', 'default')


def row_count(fname):
    """Returns number (as int) of observations in a file.

    Parameters
    ----------
    fname : path to a log file

    Notes
    -----
    Only counts data rows. Does *not* count the header as a row. Thus,
    a return value of 0 indicates a file with only the header and no data.

    """
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i


def list_data_files(stream, fpath='./', nonempty=True,
                    start_t=None, end_t=None):
    """Returns a list of filenames for specified data stream and timeframe

    Parameters
    ----------
    stream : The data stream you want.
                - 'all' produces all .csv files
                - 'accel' for accelerometer data
                - 'blue' for bluetooth data
                - 'call' for call logs
                - 'gps' for gps data
                - 'id' for (hashed) patient identifiers
                - 'log' for app log data
                - 'power' for power state data
                - 'surveyA' for survey answers
                - 'surveyT' for survey timings
                - 'text' for text logs
                - 'wifi' for wifi logs
    fpath : directory to be searched (default is current directory)
    nonempty : If True, will remove empty files from the list
    start_t : timestamp of starting time of file creation timeframe
    end_t : timestamp for ending time of file creation timeframe

    Notes
    -----
    For sanity, I check to make sure it is a .csv file, but if this hinders
    performance, it is probably not necessary. Due to this check, **voice
    recordings will not work** and will have its own function.

    Also see make_timestamp().

    """

    # First subset by data stream
    if stream == 'all':
        filelist = [f for f in os.listdir(fpath) if f.endswith('.csv')]
    else:
        filelist = [f for f in os.listdir(fpath) if
                    f.endswith('.csv') and f.startswith(stream)]

    # # add folder if not in './'
    if fpath != './':
        if fpath.endswith('/'):
            filelist = [fpath + f for f in filelist]
        else:
            filelist = [fpath + '/' + f for f in filelist]

    # # Then subset by empties (if applicable)
    if nonempty is True:
        filelist = [f for f in filelist if row_count(f) > 0]

    ## Finally, subset by time (if applicable)
    if start_t is not None and end_t is not None:
        newfilelist = []

        for name in filelist:
            try:
                file_t = int(name.split('_')[-1].split('.')[0])
                if (file_t > start_t) and (file_t < end_t):
                    newfilelist.append(name)
            except (IndexError, ValueError):
                print "error on filename ", name
        return newfilelist

    else:
        return filelist


def list_audio_files(fpath='./', start_t=None, end_t=None,
                     mp4only=False):
    """Returns a list of audio files

    Parameters
    ----------
    fpath : directory to be searched (default is current directory)
    start_t : timestamp of starting time of file creation timeframe
    end_t : timestamp for ending time of file creation timeframe
    mp4only : returns only unconverted files (mp4s)

    Notes
    -----
    Also see make_timestamp().

    """
    if mp4only is False:
        filelist = [f for f in os.listdir(fpath) if
                    f.endswith(('.mp4', '.wav'))]
    else:
        filelist = [f for f in os.listdir(fpath) if f.endswith('.mp4')]

    if fpath != './':
        if fpath.endswith('/'):
            filelist = [fpath + f for f in filelist]
        else:
            filelist = [fpath + '/' + f for f in filelist]

    if (start_t is not None) and (end_t is not None):
        newfilelist = []

        for name in filelist:
            try:
                file_t = int(name.split('_')[-1].split('.')[0])
                if (file_t > start_t) and (file_t < end_t):
                    newfilelist.append(name)
            except (IndexError, ValueError):
                print "error on filename ", name
        return newfilelist

    else:
        return filelist


def convert_mp4(fname, outname=None):
    """Uses FFmpeg to convert .mp4 file to .wav file for analysis.

    Parameters
    ----------
    fname : path and filename of .mp4 file
    outname : by default, will output a .wav file with the same name as the
                original (except for extension). Can be overwritten.

    Notes
    -----
    **DEPENDS ON FFMPEG BEING INSTALLED** since Python does not have native
    .mp4 support. Also note that **THIS SHOULD BE RUN IN INTERACTIVE PYTHON**.
    Requires input at the shell if file alreadye exists.

    If you have homebrew, try: `brew install ffmpeg`

    Else, see: https://trac.ffmpeg.org/wiki/CompilationGuide

    """
    command = 'ffmpeg -i ' + fname + ' -ab 160k -ac 2 -ar 44100 -vn '
    if outname is None:
        command = command + fname[: -4] + '.wav'
    else:
        command = command + outname

    subprocess.call(command, shell=True)


def return_file(fname):
    """Returns a file as a list with each row represented by a list

    Parameters
    ----------
    fname : path and filename of .csv file to be returned

    Notes
    -----
    Returns the entire file so the first line will always be the header. Mostly
    just a helper function for other functions.

    """
    lines = []
    for line in csv.reader(open(fname)):
        lines.append(line)
    return lines


def make_timestamp(yr, mo, dy, hr=0, mi=0, java=True):
    """Specify a UTC datetime and returns timestamp in UTC

    Parameters
    ----------
    yr : year
    mo : month [1, 12]
    dy : day
    hr : hour [0, 23]
    mi : minutes [0, 59]
    java : if True, returns Java time (in microseconds), else returns Unix time

    Notes
    -----
    Remember, all datetimes  on the phones are recorded in UTC so adjust
    appropriately.

    """

    user_time = datetime.datetime(yr, mo, dy, hr, mi)
    timestamp = calendar.timegm(user_time.timetuple())

    if java is True:
        timestamp *= 1000

    return int(timestamp)


def import_df(flist, tstamp='timestamp', setindex=True):
    """Merges files into a single pandas dataframe with UTC readable time

    Parameters
    ----------
    flist : list of files (usually generated from list_data_files())
    tstamp : name of the timestamp variable header (not all are the same)
    setindex : sets 'datetime' to the dataframe index.

    Notes
    -----
    Do not mix different data streams into the same pandas dataframe. I asked
    programmers to make all timestamp headers consistent, so we won't need
    the `tstamp` parameter.

    """
    slices = []

    # # Iterate through and append all the dataframes
    for f in flist:
        frame = pd.read_csv(f)
        slices.append(frame)

    # # Concatenate them into one large dataframe (ignore_index must be True)
    whole = pd.concat(slices, ignore_index=True)

    ## Turn timestamps into human-readable time (Remember, it's in UTC)
    whole['dt'] = [datetime.datetime.utcfromtimestamp(int(t / 1000))
                   for t in whole[tstamp]]

    ## Some headers randomly have whitespace in them. Strip.
    whole = whole.rename(columns=lambda x: x.strip())

    ## Set index to datetime for better x-axis labeling
    if setindex is True:
        whole.set_index('dt', inplace=True)

    return whole


def ts_to_local(timestamp):
    """Takes a timestamp as string or int and returns readable local time

    Notes
    -----
    See ts_to_utc() for same version printing in UTC instead of local time zone.

    MK: I also have code somewhere that does this in O(1) time, but doubt it's
    necessary here. This solution avoids another import.

    """
    if timestamp is None:
        return None
    timestamp = int(timestamp)
    if len(str(timestamp)) == 13:
        timestamp /= 1000
    return datetime.datetime.fromtimestamp(
        int(timestamp)).strftime('%m/%d/%Y %H:%M:%S')


def ts_to_utc(timestamp):
    """Takes a timestamp as string or int and returns readable UTC time

    Notes
    -----
    See ts_to_local() for same version printing in computer's local time
    instead of UTC

    """
    if timestamp is None:
        return None
    timestamp = int(timestamp)
    if len(str(timestamp)) == 13:
        timestamp /= 1000
    return datetime.datetime.utcfromtimestamp(
        int(timestamp)).strftime('%m/%d/%Y %H:%M:%S')


def plot_accel(df, start_ts=None, end_ts=None, ts_col='timestamp',
               psave=False, savename=None):
    """Plots accelerometer data.

    Parameters
    ----------
    df : a pandas.DataFrame containing accelerometer data (see import_df())
    start_ts : starting timestamp (see make_timestamp())
    end_ts : ending timestamp (see make_timestamp())
    ts_col : specify name of the timestamp column in the pandas.DataFrame
    psave : If True, saves the plot
    savename : name of the saved plot

    Notes
    -----
    Plots are prettier if you give a 2-5 minute buffer before and after your
    timestamp. For example, instead of specifying 6/2/2015 at midnight to
    6/3/2015 at midnight, do 6/1/2015 at 11:55pm and 6/4/2015 at 12:05am.

    """
    # If time slice not specified, just make a huge slice. Fix this later.
    if (start_ts is None) and (end_ts is None):
        start_ts = make_timestamp(2000, 01, 01)
        end_ts = make_timestamp(2030, 12, 31)

    # # Verify timestamps
    if len(str(start_ts) + str(end_ts)) < 25:
        print "\nInvalid timestamp(s). See make_timestamp().\n"
    else:
        # slice out data
        subdf = df[(df[ts_col] >= start_ts) & (df[ts_col] <= end_ts)]

        # plot x y z
        fig, axes = plt.subplots(nrows=3, ncols=1)
        fig.set_size_inches(8, 5)
        subdf['x'].plot(ax=axes[0], color='k', sharex=True)
        subdf['y'].plot(ax=axes[1], color='red', sharex=True)
        subdf['z'].plot(ax=axes[2], sharex=True)
        axes[0].set_ylabel(r'$\frac{m}{s^2}$')
        axes[1].set_ylabel(r'$\frac{m}{s^2}$')
        axes[2].set_ylabel(r'$\frac{m}{s^2}$')

        # it seems like there's a limit of ~[-20, 20], but not positive.
        yrange = range(-20, 21, 10)
        axes[0].yaxis.set_ticks(yrange)
        axes[1].yaxis.set_ticks(yrange)
        axes[2].yaxis.set_ticks(yrange)

        # legends
        axes[0].legend(loc=3)
        axes[1].legend(loc=3)
        axes[2].legend(loc=3)

        # x axis
        timeaxis = range(0, 25, 4)
        timelabs = ['0 h', '4 h', '8 h', '12 h', '16 h', '20 h', '0 h']
        axes[0].xaxis.set_major_locator(HourLocator(byhour=timeaxis))
        axes[1].xaxis.set_major_locator(HourLocator(byhour=timeaxis))
        axes[2].xaxis.set_major_locator(HourLocator(byhour=timeaxis))
        axes[2].xaxis.set_ticklabels(timelabs)
        axes[2].xaxis.reset_ticks()
        axes[2].set_xlabel("")

        # save?
        if psave is True:
            figure = plt.gcf()
            figure.set_size_inches(12, 6)
            if savename is None:
                plt.savefig('accel_plot.pdf', bbox_inches='tight')
            else:
                plt.savefig(savename, bbox_inches='tight')

        return fig, axes


def plot_wav(fname, channel=0, psave=False, savename=None, fext='.pdf'):
    """Takes a .wav file and plots amplitude over time.

    Parameters
    ----------
    fname : path and filename of .wav file
    channel : the wav files are encoded in stereo -- only plots 1 side. {0, 1}
    psave : save the plot as a file {True, False}
    savename : file will be saved with same name as fname unless you override
    fext : extension of file type (.pdf by default)

    """
    ## Import
    sampfreq, snd = wavfile.read(fname)

    ## Map from integers to floats [-1, 1]
    if snd.dtype is np.dtype('int16'):
        snd = snd / (2.0 ** 15)

    ## Just use one of the channels
    s1 = snd[:, channel]

    ## Make a time array and plot it
    timearray = np.arange(0, float(snd.shape[0]), 1)
    timearray = timearray / sampfreq  # convert from points to seconds
    timearray *= 1000  # convert to milliseconds

    plt.plot(timearray, s1, color='k')
    plt.ylabel('Amplitude')
    plt.xlabel('Time (ms)')
    plt.show()
    if psave is True:
        figure = plt.gcf()
        figure.set_size_inches(12, 6)
        if savename is None:
            plt.savefig(fname[:-4] + fext, bbox_inches='tight')
        else:
            plt.savefig(savename + fext, bbox_inches='tight')
        plt.close()


def describe_user(fpath='./'):
    """Creates a summary dataframe for specified users

    Parameters
    ----------
    fpath : path to the user directory

    Notes
    -----
    Assumes user directories are "as downloaded" with all csv's inside a single
    directory. I can rewrite this later to walk through subdirectories, but
    unless there's a reasonable need for this, just use standard downloads.

    Also know that the timestamps are **time of file creation**. Not first and
    last observation, but first and last file created. Some sterams do not have
    j

    """
    # # Create a list of all the files, then split to get the type of data, then
    # # turn it into a set to get unique values, then turn it into a sorted list
    ## so we can import it into a pandas.DataFrame.
    ftypes = [f.split('_')[0] for f in os.listdir(fpath) if f.endswith('.csv')]
    ftypes = list(set(ftypes))
    ftypes.sort()

    ## Get a dictionary of all stream : files pairs. Makes getting timestamps
    ## easier later on.
    flist_nonempty = {ftype: list_data_files(stream=ftype,
                                             fpath=fpath) for ftype in ftypes}
    flist_all = {ftype: list_data_files(stream=ftype,
                                        fpath=fpath, nonempty=False) for
                 ftype in ftypes}

    ## make the columns
    ## number of files, empty, and nonempty
    n_nonempty = [len(flist_nonempty[x]) for x in ftypes]
    n_files = [len(flist_all[x]) for x in ftypes]
    n_empty = list(np.subtract(n_files, n_nonempty))

    ## number of lines / observations
    n_lines = [sum(row_count(f) for f in flist_nonempty[s]) for s in ftypes]

    ## first and last time of creation (in UTC)
    ## NOTE: first and last time of observation might be worth doing, but isn't
    ## straightforward because of inconsistent column naming and order. I've
    ## talked to the programmers about fixing it. Until then, first and last
    ## nonempty data file will have to suffice.
    ## first split will get the timestamp. second split removes extension.
    ## ternary operator checks for empty list and returns None if empty.
    first = [flist_nonempty[f][0].split('_')[-1].split('.csv')[0] if
             flist_nonempty[f] else None for f in ftypes]
    last = [flist_nonempty[f][-1].split('_')[-1].split('.csv')[0] if
            flist_nonempty[f] else None for f in ftypes]
    first_ts = [ts_to_utc(x) for x in first]
    last_ts = [ts_to_utc(x) for x in last]

    d = {'all_files': n_files, 'nonempty_files': n_nonempty,
         'empty_files': n_empty, 'lines': n_lines, 'first_ts': first_ts,
         'last_ts': last_ts}
    df = pd.DataFrame(data=d, index=ftypes)
    cols = df.columns.tolist()
    cols = cols[-2:-1] + cols[:1] + cols[-1:] + cols[1:-2]
    df = df[cols]

    return df


def plot_gps(df, bounds=None, spacer=.001,
             shpfile=None, shpname=None,
             start_ts=None, end_ts=None, ts_col='time',
             res='c', proj='merc',
             dcoast = False, dbound = False,
             dscale = True, sspacer = None, slength = 1,
             psave=False, savename=None):
    """Plots users GPS points

    Parameters
    ----------
    df : a pandas.DataFrame containing GPS data (via import_df())
    bounds : lower left and upper right bounds of the basemap plot
        If specified, should be a list specifying
            [llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon]
    spacer : if bounds are not specified, the amount of buffer to
        add to min/max latitude/longitude
    shpfile : an overlay shapefile if you want (e.g., roads)
    shpname : basemaps likes it when you specify a name with your
        shp file
    start_ts : starting timestamp data slice (see make_timestamp())
    end_ts : ending timestamp data slice (see make_timestamp())
    ts_col : the name of the timestamp column. I asked programmers
        to make this consistent, but for now, specify it.
    res : resolution of basemap drawing (default is 'full')
    proj : projection of basemap plot (default is mercator)
    psave : if true, save the plot
    savename : name of the plot to be saved

    """
    # # Data stuff
    # If time slice not specified, just make a huge slice. Fix this later.
    if (start_ts is None) and (end_ts is None):
        start_ts = make_timestamp(2000, 01, 01)
        end_ts = make_timestamp(2030, 12, 31)

    df = df[(df[ts_col] >= start_ts) & (df[ts_col] <= end_ts)]

    ## Set up map
    if bounds is None:
        lllat = df.latitude.min() - spacer
        lllon = df.longitude.min() - spacer
        urlat = df.latitude.max() + spacer
        urlon = df.longitude.max() + spacer
    else:
        lllat = bounds[0]
        lllon = bounds[1]
        urlat = bounds[2]
        urlon = bounds[3]
    m = Basemap(llcrnrlat=lllat, llcrnrlon=lllon,
                urcrnrlat=urlat, urcrnrlon=urlon,
                resolution=res, projection=proj)
    if dcoast is True:
        m.drawcoastlines()
    if dbound is True:
        m.drawmapboundary(fill_color='#1C6BA0')
    m.fillcontinents(color='.95', lake_color='#1C6BA0')
    if shpfile is not None:
        if shpname is None:
            shpname = 'roads'
        m.readshapefile(shpfile, shpname)
    if dscale is True:
        if sspacer is None:
            sspacer = (lllon, lllat)
        m.drawmapscale(lat=spacer[1], lon=spacer[0],
                       lon0=df.longitude.mean(), lat0=df.latitude.mean(),
                       length=slength,
                       barstyle='fancy',
                       format='%.2f')
    x, y = m(df.longitude.values, df.latitude.values)

    ## Plotting
    plt.plot(x, y, '.', color='red', alpha=.75, ms=2)


def duplicates(df, tbuffer = 30000, calls = False):
    """Takes a call/text dataframe returns suspected duplicates.

    Parameters
    ----------
    df : a call or text dataframe created by import_df()
    tbuffer : amount of time (in milliseconds) to consider the next observation
    calls : if True, assumes call dataframe. Else, assumes text dataframe.

    Usage
    -----
    dupes = duplicates(df = text_data_frame)
    text_data_frame['dupes'] = dupes
    text_no_duplicates = text_data_frame[text_data_frame.dupes == False]

    Notes
    -----
    This is my 'good enough' solution. You should *seriously* considering making
    custom solutions based on your needs. For example, for some case uses,
    pd.DataFrame.duplicated() will be sufficient -- especially for small time
    frames. My solution will not be adequate if you need very reliable social
    data. Lastly, this solution is wildly inefficient (especially compared to
    duplicated()).

    Buyer beware.

    """
    ## Pick the correct index depending on call or text dataframe
    ## ts represents the timestamp column and ix represents the duration/length.
    if calls is True:
        ts = 2
        ix = 0
    else:
        ts = 0
        ix = 2

    ## Now we iterate through observations row by row and compare any sequential
    ## observations that fall within our specified time window. If they do,
    ## we then compare the call/text metadata and if they are identical, we
    ## assume it is a duplicate.
    dupes = []
    for i in range(len(df)):
        if i + 1 == len(df):
            test = False
        elif df.iloc[i][ts] - df.iloc[i + 1][ts] < tbuffer:
            if ((df.iloc[i][1] == df.iloc[i+1][1]) and
                (df.iloc[i][ix] == df.iloc[i+1][ix]) and
                (df.iloc[i][3] == df.iloc[i+1][3])):
                    test = True
            else:
                test = False
        dupes.append(test)
    return dupes
