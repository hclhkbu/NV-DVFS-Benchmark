import time
import datetime
import sys,urllib,urllib2
import csv
import os, glob, re
import cPickle as pickle
import numpy as np
import ConfigParser, argparse
import json
import pandas as pd

if not os.path.exists("csvs/raw"):
    os.makedirs("csvs/raw")

logRoot = 'logs'
csvRoot = 'csvs/raw'

parser = argparse.ArgumentParser()
parser.add_argument('--benchmark-setting', type=str, help='gpu benchmark setting', default='gtx980-high-dvfs')
parser.add_argument('--kernel-setting', type=str, help='kernels of benchmark', default='real-small-workload')
parser.add_argument('--core-base', type=int, help='base core frequency', default=0)
parser.add_argument('--mem-base', type=int, help='base memory frequency', default=0)

opt = parser.parse_args()
print opt

logRoot = "%s/%s-%s" % (logRoot, opt.benchmark_setting, opt.kernel_setting)

power_filelist = glob.glob(r'%s/*power.log' % logRoot)
power_filelist.sort()

# Reading metrics list
cf_bs = ConfigParser.SafeConfigParser()
cf_bs.read("configs/benchmarks/%s.cfg" % (opt.benchmark_setting))
metrics = json.loads(cf_bs.get("profile_control", "metrics"))
coreBase = json.loads(cf_bs.get("dvfs_control", "coreBase"))
memBase = json.loads(cf_bs.get("dvfs_control", "memBase"))
powerState = json.loads(cf_bs.get("dvfs_control", "powerState"))

# Read GPU application settings
cf_ks = ConfigParser.SafeConfigParser()
cf_ks.read("configs/kernels/%s.cfg" % opt.kernel_setting)
benchmark_programs = cf_ks.sections()

head = ["appName", "coreF", "memF", "argNo", "kernel", "power/W"]
print head

# prepare csv file
csvfile = open('%s/%s-%s-Power.csv' % (csvRoot, opt.benchmark_setting, opt.kernel_setting), 'wb')
csvWriter = csv.writer(csvfile, dialect='excel')

# write table head
csvWriter.writerow(head)

for fp in power_filelist:
    # print fp

    baseInfo = fp.split('_')
    appName = baseInfo[1]
    coreF = baseInfo[2][4:]
    memF = baseInfo[3][3:]
    argNo = baseInfo[4]

    kernel = json.loads(cf_ks.get(appName, 'kernels'))[0]
    rec = [appName, coreF, memF, argNo, kernel]

    # neglect first two lines of device information and table header
    f = open(fp, 'r')
    content = f.readlines()[2:]
    f.close()
    
    powerList = [float(line.split()[4].strip()) / 1000.0 for line in content if int(line.split()[1]) == powerState]
    powerList = powerList[len(powerList) / 7 * 3 :len(powerList) / 7 * 4]   # filter out those power data of cooling down GPU
    rec.append(np.mean(powerList))

    print rec
    csvWriter.writerow(rec[:len(head)])

