# -*- coding: utf-8 -*-
"""
    `beiwedata` scripts for audio data stream.
"""

import subprocess
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib

## Plot settings -- otherwise font changes at export
pd.set_option('display.mpl_style', 'default')
font = {'family': 'normal'}
matplotlib.rc('font', **font)

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
    Requires input at the shell if file already exists.

    If you have homebrew, try: `brew install ffmpeg`;
    else, see: https://trac.ffmpeg.org/wiki/CompilationGuide

    Also, never tested this on a Windows machine.

    """
    command = 'ffmpeg -i ' + fname + ' -ab 160k -ac 2 -ar 44100 -vn '
    if outname is None:
        command = command + fname[: -4] + '.wav'
    else:
        command = command + outname

    subprocess.call(command, shell=True)

def plot_wav(fname, channel=0, psave=False, savename=None, fext='.pdf'):
    """Takes a .wav file and plots amplitude over time -- returns as fig

    Parameters
    ----------
    fname : path and filename of .wav file
    channel : the wav files are encoded in stereo -- only plots 1 side. {0, 1}
    psave : save the plot as a file {True, False}
    savename : file will be saved with same name as fname unless you override
    fext : extension of file type (.pdf by default)

    Notes
    -----
    To keep this generic, I do not mess with the y-axis. Thus, it is unlikely
    to be symmetric. Adjust accordingly.

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
    fig = plt.gcf()
    if psave is True:
        fig.set_size_inches(12, 6)
        if savename is None:
            plt.savefig(fname[:-4] + fext, bbox_inches='tight')
        else:
            plt.savefig(savename + fext, bbox_inches='tight')
    return fig
