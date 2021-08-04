import tool.basicTool as bas
import tool.dbTool as dbs

import os
import sys
import json
import time
import shutil
import zipfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from requests.packages.urllib3.exceptions import InsecureRequestWarning

## Download function
def downloadFile (location, start, end, tileList):
    filePath = bas.pathWithList(['lib', 'sentinel', 'zip'])
    
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    session = requests.Session()
    url = 'https://scihub.copernicus.eu/dhus//login'
    para = { 'login_username': 'eeslab508', 'login_password': 'eeslab508'}
    login = session.post(url, params=para, verify=False)
    url = getURL (location, start, end)
    html = session.get(url)
    try:
        jsonData = json.loads(html.text)['products']
        downloadList = {}
        for data in jsonData:
            mission, level, sensingTime, baselineNum, orbitNum, tile = getDetail(data['identifier'])
            if tile in tileList:
                downloadList[data['identifier']] = data['uuid']
    except json.decoder.JSONDecodeError:
        soupData = BeautifulSoup(html.text, 'lxml').products
        downloadList = {}
        for data in soupData:
            mission, level, sensingTime, baselineNum, orbitNum, tile = getDetail(str(data.identifier)[len('identifier')+2:-len('identifier')-3])
            if tile in tileList:
                downloadList[str(data.identifier)[len('identifier')+2:-len('identifier')-3]] = str(data.uuid)[len('uuid')+2:-len('uuid')-3]
    except Exception:
        print('Web response error')
    for download in downloadList:
        url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('" + downloadList[download] + "')/$value"
        print(url)

def getURL (location, start, end):
    # The function for getting url of downloading
    url = 'https://scihub.copernicus.eu/dhus/api/stub/products?filter='
    loc = '( footprint:"Intersects(POLYGON(('
    pos = '( '
    oth = '( (platformname:Sentinel-2 AND filename:S2B_* ) )&offset=0&limit=125&sortedby=ingestiondate&order=desc'
    # check -------
    ### location
    try:
        for i in range(len(location)):
            loc = loc + str(location[i][0]) + ' ' + str(location[i][1])
            if i != len(location)-1:
                loc = loc + ','
            else:
                loc = loc + ')))")'
    except IndexError:
        print('Input location error!')
        sys.exit(1)
    ### date
    if start[4] != '-' or start[7] != '-' or end[4] != '-' or end[7] != '-' or len(start) != 10 or len(end) != 10:
        print('Please check date format!! format: YYYY-mm-dd')
        sys.exit(1)
    try:
        date = {
            'start': {
                'Y': int(start[0:4]),
                'm': int(start[5:7]),
                'd': int(start[8:10])
            },
            'end': {
                'Y': int(end[0:4]),
                'm': int(end[5:7]),
                'd': int(end[8:10])
            }
        }
    except ValueError:
        print('Please check input date')
        sys.exit(1)

    now = datetime.now()
    for j in date:
        for i in date[j]:
            if date[j][i] > int(now.strftime('%'+i)):
                print(date[j])
                print(now.strftime('%'+i))
                print('The date must be a past date!')
                sys.exit(1)
            elif i == 'Y' or i == 'm':
                break;

    for i in date['start']:
        if date['start'][i] > date['end'][i]:
            print('Start date must be earlier than end date! ')
            sys.exit(1)
    
    t = start+'T00:00:00.000Z TO '+end+'T23:59:59.999Z'
    pos = pos + 'beginPosition:[' + t + '] AND endPosition:[' + t + '] )'
    
    return url + ' AND '.join([loc, pos, oth])

def getDetail (sentinelName):
    detail = sentinelName.split('_')
    return detail[0], detail[1], detail[2], detail[3], detail[4], detail[5]
## Upgrade sentinel
def upgradeSentinel ():
    hisPath = bas.pathWithList(['lib', 'database']) + 'processingHis.xlsx'
    archive = dbs.readExcel(hisPath)
    archiveHis = archive['name'].values
    archiveDirectory = bas.pathWithList(['lib', 'sentinel','zip'])
    fileDirectory = bas.pathWithList(['lib', 'sentinel','processing'])
    archiveFile = []
    for file in os.listdir(archiveDirectory):
        if file not in archiveHis:
            print('Zipping: ', file)
            archiveFile.append(file)
            with zipfile.ZipFile(archiveDirectory + file) as z:
                z.extractall(fileDirectory)
    if os.listdir(fileDirectory):
        os.system("for /D %s in (" + fileDirectory + "S2B_MSIL1C*) do " + bas.pathWithList(['lib', 'exe', 'Sen2Cor-02.08.00-win64'])  + "L2A_process %s")
    for file in archiveFile:
        shutil.rmtree(fileDirectory + file[0:-4] + '.SAFE')
    timeList = []
    for file in os.listdir(fileDirectory):
        timeData = file.split('_')[2]
        if timeData not in timeList:
            timeList.append(timeData)
    # write history 
    dataset = archive.values.tolist()
    for data in archiveFile:
        dataset.append([time.strftime("%Y%m%d %H:%M:%S"), data])
    columns = ['time', 'name']
    dbs.writeExcel(dataset, columns, hisPath)
    return timeList

def getL1ABand ():
    return ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B8A', 'AOT', 'SCL', 'TCI', 'WVP']

def getL1AJP2 (timeData):
    fileDirectory = bas.pathWithList(['lib', 'sentinel','processing'])
    jp2Path = bas.pathWithList(['lib', 'sentinel','raw', timeData[0:8] + 'B'])
    bas.createFolder(jp2Path)
    bas.createFolder(jp2Path+'warp\\')
    tileList = []
    for file in os.listdir(fileDirectory):
        if file.split('_')[2] == timeData:
            if file.split('_')[5] not in tileList:
                tileList.append(file.split('_')[5])
            dirName = fileDirectory + file + '\\GRANULE\\'
            dirName = dirName + os.listdir(dirName)[0] + '\\IMG_DATA\\'
            for resolution in ['R10m\\', 'R20m\\', 'R60m\\']:
                filePath = dirName + resolution
                for jp2 in os.listdir(filePath):
                    if not os.path.exists(jp2Path + jp2):
                        os.replace(filePath + jp2, jp2Path + jp2)
            shutil.rmtree(fileDirectory + file)
    fileList = [tile + '_' + timeData + '_' for tile in tileList]
    noBand = generateWarpData (jp2Path, fileList)
    print(noBand)

def generateWarpData (fileDir, fileList):
    warpPath = fileDir + 'warp\\'
    noBand = []
    for band in getL1ABand():
        for f in fileList:
            if os.path.exists(fileDir + f + band +'_10m' + '.jp2'):
                fileName = f + band +'_10m' + '.jp2'
            elif os.path.exists(fileDir + f + band +'_20m' + '.jp2'):
                fileName = f + band +'_20m' + '.jp2'
            elif os.path.exists(fileDir + f + band +'_60m' + '.jp2'):
                fileName = f + band +'_60m' + '.jp2'
            else:
                if band not in noBand:
                    noBand.append(band)
                fileName = '-1'
            if fileName != '-1':
                if not os.path.exists(warpPath + f + band + '.jp2'):
                    shutil.copy(fileDir + fileName, warpPath + f + band + '.jp2')
    return noBand

bandList = getL1ABand()
