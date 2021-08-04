import os
import sys
import shutil
import pathlib
import platform

import tool.imageTool as img

## get system
def getOS ():
    return platform.uname().system

def getRootDir ():
    tmp = str(pathlib.Path(__file__).parent.absolute()).split(getFileSep()[0])
    path = tmp[0]
    for t in tmp[1:-2]:
        path = path + getFileSep() + t
    return path

def getFileSep ():
    system = getOS()
    if system == 'Windows':
        return '\\'
    elif system == 'Linux':
        return '//'

## create
def createFolder(directory):
    if not os.path.exists(directory):
        print('Create directory: ', directory)
        os.makedirs(directory)
    return directory

def copyFile (source, destination, fileName):
    if not os.path.exists(destination + fileName):
        dest = shutil.copyfile(source + fileName, destination + fileName)
        print('File : ' + fileName + ' copy to ' + dest)
    else:
        print('File : ' + destination + fileName + 'is existed.')

## content
def getDirList (path):
    return os.listdir(path)

def checkDir (path):
    return os.path.isdir(path)

def getDomainFile (domainName, fileType):
    if fileType == 'tif':
        return pathWithList(['datasets', domainName]) + domainName + '.tif'
    elif fileType == 'shp':
        return pathWithList(['domainShp']) + domainName + '.shp'
    elif fileType == 'dem':
        return pathWithList(['datasets', domainName]) + domainName + '_dem.tif'
## path
def pathWithList (nameList):
    if isinstance(nameList, list):
        nameList.append('')
        return rootDir + fileSep.join(nameList)
    print('The parameter of pathWithList() must be list!!!')
    sys.exit()

## set out
fileSep = getFileSep()
rootDir = getRootDir() + fileSep

lat = str(24.1378)
lon = str(120.7288)
domainName = '51N'
domainSplit = ['Center', 'West', 'East']
if domainSplit != []:
    domainList = [domainName + '_' + d for d in domainSplit]
else:
    domainList = [domainName]
for d in domainList:
    if d not in getDirList(pathWithList(['datasets'])):
        createFolder(pathWithList(['datasets', d]))
        createFolder(pathWithList(['datasets', d, 'topographic']))
        TW_dem = pathWithList(['lib', 'dem']) + 'dem_20m.tif'
        domainShp = getDomainFile(d, 'shp')
        domainDem = getDomainFile(d, 'dem')
        domainTif = getDomainFile(d, 'tif')
        img.clipImg(TW_dem, domainShp, domainDem)
        img.shp2tif (domainShp, domainDem, domainTif)
        

dataList = ['20180327', '20180625', '20180903', '20181202']
tileList = ['T51RUH', 'T51QUG', 'T51QTG']