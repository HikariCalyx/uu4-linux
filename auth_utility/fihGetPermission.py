#!/usr/bin/python3
# HCTSW Care Unlock Utility 4 for Linux - Python Service Permission Granting Program
# 2015-2024 (C) Hikari Calyx Tech. All Rights Reserved.
# Version: 1.1.231219-2049

import os
import sys
import base64
import requests
import json
import argparse
import hashlib
from pyfastboot import fastboot

# Self-Checksum
comppath = os.path.abspath(__file__)
with open(comppath, 'r') as f:
    selfcode = f.read().encode('utf8')
    self_checksum = hashlib.new('sha256', selfcode).hexdigest()

api_baseurl = 'https://api.hikaricalyx.com'
sec4_url = '/uu4/v3/GetSignature4'
sec8_url = '/uu4/v3/GetSignature8'
sec9_url = '/uu4/v3/GetSignature9'

# Definitions

# File Path Definition
if sys.platform.startswith('win32'):
    credPath = os.getenv('systemdrive') + '/Temp/'
    if not os.path.exists(credPath):
        os.makedirs(credPath)
elif sys.platform.startswith('darwin'):
    credPath = os.getenv('TMPDIR') + '/ostremote/'
    os_lang = os.getenv('LANG')
elif sys.platform.startswith('freebsd'):
    credPath = os.getenv('TMPDIR') + '/ostremote/'
    os_lang = os.getenv('LANG')
else:
    credPath = '/tmp/ostremote/'
    os_lang = os.getenv('LANG')

if not os.path.exists(credPath):
    os.makedirs(credPath)

# Read Parameters necessary for verification

parser = argparse.ArgumentParser(description='DO NOT EDIT')
parser.add_argument('--uu4hash', default='0000000000000000000000000000000000000000000000000000000000000000',
                    help='hashKey')
args = parser.parse_args()
uu4_main_checksum = args.uu4hash

# Request Header
req_header = {'Content-Type': 'application/json', 'User-Agent': 'HCTSW-UU4-PYTHON-' + uu4_main_checksum[0:4] + self_checksum[0:4] + '/1.0'}

# Convert hex digest into base64
def digestToB64(digest):
    requestDigest = base64.b64encode(bytes.fromhex(digest)).decode('utf8')
    return(requestDigest)

# Get ESNs
def getESN():
    try:    
        imei1 = device.Getvar('imei_1').decode('utf8')
        imei2 = device.Getvar('imei_2').decode('utf8')
        meid = device.Getvar('meid').decode('utf8')
    except:
        imei1 = ''
        imei2 = ''
        meid = ''
    returnMessage = [imei1, imei2, meid]
    return(returnMessage)

# Generate Security Version Message
def sec4Message(project, psn, imei1, imei2, meid, digest, servType):
    message = {
        'prjcode': project,
        'psn': psn,
        'imei1': imei1,
        'imei2': imei2,
        'meid': meid,
        'digest': digest,
        'type': servType,
        'skuid': 'auto',
        'mlffile': 'UU4-Linux.mlf',
        'frp': '1'
    }
    return(message)

def sec8Message(project, psn, imei1, imei2, meid, brand, digest, servType):
    message = {
        'prjcode': project,
        'psn': psn,
        'imei1': imei1,
        'imei2': imei2,
        'meid': meid,
        'brand': brand,
        'digest': digest,
        'type': servType,
        'skuid': 'auto',
        'mlffile': 'UU4-Linux.mlf',
        'frp': '1'
    }
    return(message)

# Service Permission Message

def displayInformation4(ver, servType, project, psn, digest):
    print('')
    print('Security Version: 000' + ver + '\nProject Code: ' + project + '\nPSN: ' + psn)
    if servType == 'v':
        print('DM-Veracity Challenge: ' + digest)
    elif servType == 'u':
        print('UID: ' + digest)
    print('')

def displayInformation8(ver, servType, project, brand, psn, digest):
    print('')
    print('Security Version: 000' + ver + '\nBrand Code: ' + brand + '\nProject Code: ' + project + '\nPSN: ' + psn)
    if servType == 'v':
        print('DM-Veracity Challenge: ' + digest)
    elif servType == 'u':
        print('UID: ' + digest)
    print('')

def grantPermission(servType, path):
    result0 = device.Download(path)
    if servType == 'v':
        result1 = device.Flash('veracity').decode('utf8')
        if 'FAIL' in result1:
            return([False, '00000002'])
        else:
            return([True, '00000000'])
    elif servType == 'u':
        result1 = device.Flash('encUID')
        result2 = device.Oem('selectKey service')
        result3 = device.Oem('doKeyVerify').decode('utf8')
        if 'FAIL' in result3:
            return([False, '00000002'])
        else:
            return([True, '00000000'])

def getSignature4(servType, project, psn, digest):
    if servType == 'v':
        filename = 'veracity_sec4-' + project + '-' + digest + '.bin'
    elif servType == 'u':
        filename = 'encuid_sec4-' + project + '-' + digest + '.bin'
    if os.path.exists(credPath + filename):
        result = grantPermission(servType, credPath + filename)
        return(result)
    else:
        reqDigest = digestToB64(digest)
        esn = getESN()
        requestMessage = sec4Message(project, psn, esn[0], esn[1], esn[2], reqDigest, servType)
        result = requests.post(api_baseurl+sec4_url, data=json.dumps(requestMessage), headers=req_header).text
        result_dict = json.loads(result)
        if result_dict['status'] == 'Fail':
            errorcode = result_dict['code']
            return([False, errorcode])
        else:
            reqSignBinary = base64.b64decode(result_dict['signature'])
            with open(credPath + filename, 'wb') as sign:
                sign.write(reqSignBinary)
            result = grantPermission(servType, credPath + filename)
            return(result)

def getSignature8(servType, project, brand, psn, digest):
    if servType == 'v':
        filename = 'veracity_sec8-' + brand + '-' + project + '-' + psn + '-' + digest + '.bin'
    elif servType == 'u':
        filename = 'encuid_sec8-' + brand + '-' + project + '-' + psn + '-' + digest + '.bin'
    if os.path.exists(credPath + filename):
        result = grantPermission(servType, credPath + filename)
        return(result)
    else:
        reqDigest = digestToB64(digest)
        esn = getESN()
        requestMessage = sec8Message(project, psn, esn[0], esn[1], esn[2], brand, reqDigest, servType)
        result = requests.post(api_baseurl+sec8_url, data=json.dumps(requestMessage), headers=req_header).text
        result_dict = json.loads(result)
        if result_dict['status'] == 'Fail':
            errorcode = result_dict['code']
            return([False, errorcode])
        else:
            reqSignBinary = base64.b64decode(result_dict['signature'])
            with open(credPath + filename, 'wb') as sign:
                sign.write(reqSignBinary)
            result = grantPermission(servType, credPath + filename)
            return(result)

def getSignature9(servType, project, brand, psn, digest):
    if servType == 'v':
        filename = 'veracity_sec9-' + brand + project + psn + digest + '.bin'
    elif servType == 'u':
        filename = 'encuid_sec9-' + brand + project + psn + digest + '.bin'
    if os.path.exists(credPath + filename):
        result = grantPermission(servType, credPath + filename)
        return(result)
    else:
        reqDigest = digestToB64(digest)
        esn = getESN()
        requestMessage = sec8Message(project, psn, esn[0], esn[1], esn[2], brand, reqDigest, servType)
        result = requests.post(api_baseurl+sec9_url, data=json.dumps(requestMessage), headers=req_header).text
        result_dict = json.loads(result)
        if result_dict['status'] == 'Fail':
            errorcode = result_dict['code']
            return([False, errorcode])
        else:
            reqSignBinary = base64.b64decode(result_dict['signature'])
            with open(credPath + filename, 'wb') as sign:
                sign.write(reqSignBinary)
            result = grantPermission(servType, credPath + filename)
            return(result)

# Init Fixed Variables
sec8_prjWorkaround = ['EAG', 'RHD']
sec9_prjWorkaround = ['OJ6']

# Init Device Variables
device = fastboot.FastbootCommands()
initDevice = device.ConnectDevice()
psnBin = device.Getvar('productid')
psn = psnBin.decode('utf8')
try:
    secVer = device.Oem('getSecurityVersion').decode('utf8')
    blType = device.Oem('getBootloaderType').decode('utf8')
except:
    secVer = '0001'
    blType = 'commercial'


# Getting Permission Code
if secVer == '0001':
    if blType == 'commercial':
        digestChallenge = hashlib.new('md5', psnBin).hexdigest()
        device.Oem('dm-verity ' + digestChallenge)
        processResult = ['0']
    if blType == 'service':
        prjCode = device.Oem('getProjectCode').decode('utf8')
        digestChallenge = device.Oem('getUID').decode('utf8').replace('\n','').replace('\r','')
        servType = 'u'
        displayInformation4('1', servType, prjCode, psn, digestChallenge)
        processResult = getSignature4(servType, prjCode, psn, digestChallenge)
elif secVer == '0004':
    prjCode = device.Oem('getProjectCode').decode('utf8')
    if blType == 'commercial':
        digestChallenge = device.Oem('dm-veracity').decode('utf8').replace('\n','').replace('\r','')
        servType = 'v'
    elif blType == 'service':
        digestChallenge = device.Oem('getUID').decode('utf8').replace('\n','').replace('\r','')
        servType = 'u'
    displayInformation4('4', servType, prjCode, psn, digestChallenge)
    processResult = getSignature4(servType, prjCode, psn, digestChallenge)
elif secVer == '0008':
    if psn[0:3] not in sec8_prjWorkaround:
        prjCode = device.Oem('getProjectCode').decode('utf8')
    else:
        prjCode = psn[0:3]
    brand = device.Oem('getBrandCode').decode('utf8')
    if blType == 'commercial':
        digestChallenge = device.Oem('dm-veracity').decode('utf8').replace('\n','').replace('\r','')
        servType = 'v'
    elif blType == 'service':
        digestChallenge = device.Oem('getUID').decode('utf8').replace('\n','').replace('\r','')
        servType = 'u'
    displayInformation8('8', servType, prjCode, brand, psn, digestChallenge)
    processResult = getSignature8(servType, prjCode, brand, psn, digestChallenge)
elif secVer == '0009':
    if psn[0:3] not in sec9_prjWorkaround:
        prjCode = device.Oem('getProjectCode').decode('utf8')
    else:
        prjCode = psn[0:3]
    brand = device.Oem('getBrandCode').decode('utf8')
    if blType == 'commercial':
        digestChallenge = device.Oem('dm-veracity').decode('utf8').replace('\n','').replace('\r','')
        servType = 'v'
    elif blType == 'service':
        digestChallenge = device.Oem('getUID').decode('utf8').replace('\n','').replace('\r','')
        servType = 'u'
    displayInformation8('9', servType, prjCode, brand, psn, digestChallenge)
    processResult = getSignature9(servType, prjCode, brand, psn, digestChallenge)

if processResult[0]:
    sys.exit(0)
else:
    sys.exit(int(processResult[1]))
