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

Result will be returned into variable ```$?``` or ```%ERRORLEVEL%```. If value is 0 then service permission granted, otherwise permission granting fails.
Following image is an example of service permission granting fails if a wrong uu4hash value is provided.

![photo_2022-07-09_14-08-37](https://user-images.githubusercontent.com/29157608/184521620-31dc9f9e-da6c-4c83-91a0-0b2ff70d2fd3.jpg)

## Get Started for Bootloader Unlock Service under Linux

- [Request Bootloader Unlock from our website.](https://hikaricalyx.com/product/nokia-direct-ubl-service/)

> If you provide wrong info during request, please contact us immediately.

- Clone this repository, and [Download UU4 for Windows](https://hikaricalyx.com/how-to-use-uu4) as well (you need necessary files inside):
```
git clone https://github.com/HikariCalyx/uu4-linux
```

- Install necessary dependencies (we assume you have ADB / Fastboot binaries installed if you're using AMD64 platform, otherwise install yourself if you haven't)
```
cd uu4-linux
sudo bash install.sh
```
For macOS users, you must install homebrew before you proceed, and you should only install prerequisites without ```sudo```.

- Boot the phone into Download mode when USB debugging enabled:
```
adb reboot bootloader
fastboot devices
```

If your phone is detected:
```
cd ~/path/to/auth_utility
python3 checkOrder.py --uu4hash 1234 --mode check
```

This will check if your phone has been recorded properly on our website, if yes it will return like this. ```orderStatus``` must be ```processing``` to allow you proceed to bootloader procedure.
```
{'orderNumber': 'HCT-5555', 'orderStatus': 'processing'}
```


- In this case, if you're using Nokia 6.1 Plus with Android 10 firmware installed:
```
python3 getPermission.py --uu4hash 1234
fastboot flash abl ~/path/to/uu4-windows/bootloader_image/SDM660-835/DRG-4/abl_service.elf
fastboot flash xbl ~/path/to/uu4-windows/bootloader_image/SDM660-835/DRG-4/xbl_service.elf
fastboot reboot-bootloader
python3 getPermission.py --uu4hash 1234
fastboot oem fih on
fastboot oem devlock allow_unlock
fastboot flashing unlock
```
> WARNING: IF YOU ARE USING OTHER MODELS, DO NOT FLASH EXACTLY SAME ABL/XBL FILES!

Then, confirm bootloader unlock on your phone.
