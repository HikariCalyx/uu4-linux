#!/bin/bash
# HCTSW Care UU4 Prerequisites Installer
# 2015-2022 (C) Hikari Calyx Tech. All Rights Reserved.

# Chinese users who cannot access Github or Pypi properly should do following changes:
# 1. Replace "github.com" into "hub.fastgit.xyz" for faster Github Access. 
# 2. Reconfigure Pypi mirror server with sudo - example:
# https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
#
# Contributions on this Installation script are welcome.

basepath=$(
    cd $(dirname $0)
    pwd
)

processor_architecture=$(uname -m)

distro_check() {
    if [ -f "/usr/bin/yum" ] && [ -d "/etc/yum.repos.d" ]; then
        flavor="redhat_old"
    elif [ -f "/usr/bin/dnf" ] && [ -d "/etc/dnf.repos.d" ]; then
        flavor="redhat_new"
    elif [ -f "/usr/bin/apt" ] && [ -f "/usr/bin/dpkg" ]; then
        flavor="debian"
    elif [ -f "/usr/bin/pacman" ]; then
        flavor="arch"
    elif [ -f "/usr/bin/zypper" ]; then
        flavor="suse"
    elif [ $(uname) = Darwin ]; then
        flavor="darwin"
    fi
}

debian_inst() {
    echo -e "Debian-based distro detected. Installing prerequisites..."
    apt update
    apt -y install wget python3 git libusb-1.0-0 build-essential libssl-dev swig python3-pip python3-dev p7zip openssl unzip gawk sed uuid jq curl
    if [[ "armhf,arm64.aarch64,i686,i486,i386" =~ "$processor_architecture" ]]; then
        apt -y install android-sdk-platform-tools
    fi
}

redhat_old_inst() {
    echo -e "Redhat-based distro detected. Installing prerequisites..."
    yum update
    yum -y install wget python3 git libusb make automake gcc gcc-c++ kernel-devel openssl-devel swig python3-pip python3-devel p7zip openssl unzip gawk sed uuid jq curl
    if [[ "armhf,arm64.aarch64,i686,i486,i386" =~ "$processor_architecture" ]]; then
        yum -y install android-sdk-platform-tools
    fi
}

redhat_new_inst() {
    echo -e "Redhat-based distro detected. Installing prerequisites..."
    dnf update
    dnf -y install wget python3 git libusb-1 make automake gcc gcc-c++ kernel-devel openssl-devel swig python3-pip python3-devel p7zip openssl unzip gawk sed uuid jq curl
    if [[ "armhf,arm64.aarch64,i686,i486,i386" =~ "$processor_architecture" ]]; then
        dnf -y install android-tools
    fi
}

arch_inst() {
    echo -e "Arch-based distro detected. Installing prerequisites..."
    pacman -Sy wget python3 git libusb base-devel swig python-pip p7zip unzip gawk sed jq curl
    if [[ "armhf,arm64.aarch64,i686,i486,i386" =~ "$processor_architecture" ]]; then
        pacman -Sy android-sdk-platform-tools
    fi
}

suse_inst() {
    echo -e "SUSE-based distro detected. Installing prerequisites..."
    zypper -y install dnf -y install wget python3 git libusb gcc gcc-c++ kernel-devel libopenssl-devel swig python3-pip python3-devel p7zip openssl unzip gawk sed uuid jq curl
    if [[ "armhf,arm64.aarch64,i686,i486,i386" =~ "$processor_architecture" ]]; then
        zypper -y install android-tools
    fi
}

darwin_inst() {
    echo -e "macOS detected. Installing prerequisites..."
    # Contribute is welcome here
}

edlclient_inst() {
    echo -e "Cloning latest Qualcomm EDL client..."
    git clone https://github.com/bkerler/edl ${basepath}/bin/common/edl/qcedl/
    echo -e "Cloning latest MediaTek EDL client..."
    git clone https://github.com/bkerler/mtkclient ${basepath}/bin/common/edl/mtkclient/
    echo -e "Installing both EDL client..."
    pip3 install -r ${basepath}/bin/common/edl/qcedl/requirements.txt
    cd ${basepath}/bin/common/edl/qcedl/
    python3 setup.py build
    python3 setup.py install
    cd ${basepath}/bin/common/edl/mtkclient/
    python3 setup.py build
    python3 setup.py install
    cd ${basepath}
}

common_inst() {
    echo -e "Configuring udev rules..."
    wget https://github.com/bkerler/edl/raw/master/Drivers/50-android.rules -O /etc/udev/rules.d/50-android.rules
    wget https://github.com/bkerler/edl/raw/master/Drivers/51-edl.rules -O /etc/udev/rules.d/51-edl.rules
    udevadm control --reload-rules
    udevadm trigger
}

pyadb_inst() {
    echo -e "Installing Python ADB..."
    git clone "https://github.com/google/python-adb" ${basepath}/bin/common/pyadb
    pip3 install -r requirements.txt
    cd ${basepath}/bin/common/pyadb/
# Bugfix Part
    sed -i "s|source_file = open(source_file)|source_file = open(source_file, mode='rb')|g" adb/fastboot.py
    python3 setup.py install
    cd ${basepath}
    type pyfastboot >/dev/null 2>&1
    if [[ "$?" == "1" ]]; then
        echo -e "WARNING: Python-ADB is installed but cannot be used yet. Please add following path into PATH variable: "
        echo -e "~/.local/bin"
    fi
}

sucheck() {
    if [[ ! "$(whoami)" == "root" ]]; then
        echo -e "Please run this script with sudo or root account! "
        exit 1
    fi
}

edl_confirm() {
    read -p "Would you like to install EDL support? [Y/n]" choice_edl
    case "$choice_edl" in
    Y | y)
        edlclient_inst
        ;;
    N | n) ;;

    *)
        edl_confirm
        ;;
    esac
}

prereq_confirm() {
    read -p "Would you like to proceed? [Y/n]" choice_pr
    case "$choice_pr" in
    Y | y) ;;

    N | n)
        exit
        ;;
    *)
        prereq_confirm
        ;;
    esac
}

echo -e "HCTSW Care Unlock Utility 4 for UNIX Prerequisites Installer"
echo -e "2015-2022 (C) Hikari Calyx Tech. All Rights Reserved."
echo -e ""
sucheck
echo -e "This script will install prerequisites required by HCTSW Care UU4. "
prereq_confirm
distro_check
${flavor}_inst
common_inst
pyadb_inst
echo -e ""
echo -e "All done! Enjoy it."
echo -e ""
