#!/usr/bin/python3
# HCTSW Care Unlock Utility 4 for Linux - Python Order Check
# 2015-2022 (C) Hikari Calyx Tech. All Rights Reserved.
# Version: 1.0.220709-1544

import os
import sys
import requests
import json
import argparse
import hashlib
from adb import fastboot

paymentStatusCode = {
    'processing': 0,
    'completed': 1
}

# Self-Checksum
comppath = os.path.abspath(__file__)
with open(comppath, 'r') as f:
    selfcode = f.read().encode('utf8')
    self_checksum = hashlib.new('sha256', selfcode).hexdigest()

api_baseurl = 'https://api.hikaricalyx.com'
checkorder_url = '/ubl/v3/QueryPayment'
finalizeorder_url = '/ubl/v3/OrderFinalize'

# Definitions
# Read Parameters necessary for verification

parser = argparse.ArgumentParser(description='DO NOT EDIT')
parser.add_argument('--uu4hash', default='0000000000000000000000000000000000000000000000000000000000000000',
                    help='hashKey')
parser.add_argument('--mode', help='check, finalize')
parser.add_argument('--flag', help='unlock status')
parser.add_argument('--orderid', help='orderid')
args = parser.parse_args()
uu4_main_checksum = args.uu4hash
uu4_mode = args.mode
if uu4_mode == 'finalize':
    uu4_id = args.orderid
    uu4_flag = args.flag

# Request Header
req_header = {'Content-Type': 'application/json', 'User-Agent': 'HCTSW-UU4-LINUX-' + uu4_main_checksum[0:4] + self_checksum[0:4] + '/1.0'}

# paymentCheck
def checkOrder(psn, product):
    requestMessage = {'psn': psn, 'project': product}
    result = requests.post(api_baseurl+checkorder_url, data=json.dumps(requestMessage), headers=req_header).text
    result_dict = json.loads(result)
    if result_dict['status'] == 'Fail':
        errorcode = result_dict['code']
        return([False, errorcode, 'HCT-0000', 'unspecified'])
    else:
        orderNumber = result_dict['orderNumber']
        paymentStatus = result_dict['paymentStatus']
        if paymentStatus != 'processing':
            return([False, paymentStatusCode[paymentStatus], orderNumber, paymentStatus])
        else:
            return([True, paymentStatusCode[paymentStatus], orderNumber, paymentStatus])

def finalizeOrder(psn, orderNumber, unlockFlag):
    requestMessage = {
        'psn': psn,
        'orderNumber': orderNumber,
        'unlockFlag': unlockFlag
    }
    result = requests.post(api_baseurl+checkorder_url, data=json.dumps(requestMessage), headers=req_header).text
    result_dict = json.loads(result)
    if result_dict['status'] == 'Fail':
        errorcode = result_dict['code']
        return([False, errorcode, 'HCT-0000', 'invalid'])
    else:
        orderNumber = result_dict['orderNumber']
        paymentStatus = result_dict['paymentStatus']
        if paymentStatus != 'processing':
            return([False, paymentStatusCode[paymentStatus], orderNumber, paymentStatus])
        else:
            return([True, paymentStatusCode[paymentStatus], orderNumber, paymentStatus])

# Init Device Variables
device = fastboot.FastbootCommands()
initDevice = device.ConnectDevice()
psnBin = device.Getvar('productid')
psn = psnBin.decode('utf8')
product = device.Getvar('product').decode('utf8')

if uu4_mode == 'check':
    processResult = checkOrder(psn, product)
elif uu4_mode == 'finalize':
    processResult = finalizeOrder(psn, uu4_id, uu4_flag)
else:
    processResult = [False, '00000102', 'HCT-0000', 'unspecified']
processResultEx = {'orderNumber': processResult[2], 'orderStatus': processResult[3]}
if processResult[0]:
    print(processResultEx)
    sys.exit(0)
else:
    print(processResultEx)
    sys.exit(int(processResult[1]))
