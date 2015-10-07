# Introduction

`download_script` is the script designed for accessing, downloading, and decrypting `beiwe` data. It was created by the programmers of Beiwe, Zagaran. This version is `September 2015`.

This script is **not** intended to be a module. Instead, use `ipython` and run it via `%run ./download_script/download_script.py` or your preferred interactive method. It does **not** need to be a subdirectory of `./beiwedata/` to run properly and can exist anywhere as long as both the script and the credential file are together.

`download_script_credentials.py` will need to be customized by each researcher for their own study with their specific credentials. To prevent accidental uploads of active credentials, I have included a **blank** credential file called `EXAMPLE download_script_credentails.py`. Just duplicate this file, remove "EXAMPLE" from the file name, open the file, and put in the correct credentails. 
