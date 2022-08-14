# UU4 for Linux
Bootloader Unlock Utility 4 for Linux

## Supported OS
Any modern Linux distros should work, including Debian, Ubuntu, Deepin/UOS, Arch, Fedora, openSuSE Tumbleweed - even Crostini under Chrome OS works.
macOS and other BSD distros are untested.

We don't recommend you to run it under WSL.

## Missing Feature from UU4 for Windows
* Magisk Root Installation feature. If you're using Linux you should know how to install Magisk root yourself easily.

## About getPermission.py
* It's Python based service permission granting library. Once you have required dependencies and your phone is authorized under our server, you can run it individually like this (note #### means any hex digits with at least 4 bytes length):
```python3 getPermission.py --uu4hash ####```
Result will be returned as ```$?``` or ```%ERRORLEVEL%```. If value is 0 then service permission granted, otherwise permission granting fails.
