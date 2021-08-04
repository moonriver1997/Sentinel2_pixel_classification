import tool.basicTool as bas
import tool.imageTool as img

import ast
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import struct
from osgeo import gdal, gdalconst, ogr, osr

def waterPixelNum (waterPath):
    waterImg = img.readImg(waterPath)
    waterArr = img.flatArray(waterImg)
    return list(waterArr).count(1)

def evaluate(trueFile, dataFile, domainFile):
    trueData = gdal.Open(trueFile, gdal.GA_ReadOnly)
    trueBand = trueData.GetRasterBand(1)
    data = gdal.Open(dataFile, gdal.GA_ReadOnly)
    dataBand = data.GetRasterBand(1)
    domain = gdal.Open(domainFile, gdal.GA_ReadOnly)
    domainBand = domain.GetRasterBand(1)

    errPix = 0
    allPix = 0
    numLines = trueBand.YSize
    for line in range(numLines):
        scanlineTrue = trueBand.ReadRaster(0, line, trueBand.XSize, 1, trueBand.XSize, 1, gdal.GDT_Float32)
        tupleTrue = struct.unpack('f' * trueBand.XSize, scanlineTrue)
        scanlineData = dataBand.ReadRaster(0, line, dataBand.XSize, 1, dataBand.XSize, 1, gdal.GDT_Float32)
        tupleData = struct.unpack('f' * dataBand.XSize, scanlineData)
        scanlineDomain = domainBand.ReadRaster(0, line, domainBand.XSize, 1, domainBand.XSize, 1, gdal.GDT_Float32)
        tupleDomain = struct.unpack('f' * domainBand.XSize, scanlineDomain)
        for i in range(len(tupleTrue)):
            if tupleDomain[i] > 0:
                allPix = allPix + 1
                if tupleTrue[i] > 0:
                    trueVal = 1
                else:
                    trueVal = 0
                
                if tupleData[i] > 0:
                    dataVal = 1
                else:
                    dataVal = 0

                if trueVal != dataVal:
                    val = 1
                    errPix = errPix + 1
            else:
                val = 0

    print(dataFile, errPix, allPix)
    trueBand = None
    dataBand = None

    return errPix/allPix, errPix, allPix

def figCreate():
    mpl.rcParams['font.family'] = 'Consolas'
    mpl.rcParams['font.size'] = 8
    # mpl.rcParams['figure.figsize'] = [2, 2]
    fig, ax = plt.subplots(2, 1)
    fig.subplots_adjust(hspace=0.3)
    return fig, ax

def processHistoryData (filePath, fileName):
    # keyList = ['model', 'score', 'pixelNum', 'history']
    # hisList = ['val_loss', 'val_accuracy', 'loss', 'accuracy']
    data = readTrainHis(filePath + fileName)
    modelName = data['model'].split(bas.fileSep)[-1][:-3]
    fig, ax = figCreate()
    fig.suptitle(modelName)
    ax[0].set_title("accuracy")
    ax[0].plot(data['history']['accuracy'], color='blue', label='train')
    ax[0].plot(data['history']['val_accuracy'], color='red', label='validation')
    ax[0].set_ylim(0.9, 1.1)
    ax[0].legend()
    ax[1].set_title("loss")
    ax[1].plot(data['history']['loss'], color='blue', label='train')
    ax[1].plot(data['history']['val_loss'], color='red', label='validation')
    ax[1].legend()

    plt.xlabel('Epoch')
    plt.savefig(filePath + 'plot' + bas.fileSep + modelName + '.png')
    plt.close('all')
    # plt.show()
    return modelName, len(data['history']['val_loss']), data['pixelNum'], data['score']

def readTrainHis (fileName):
    file = open(fileName, "r")

    contents = file.read()
    dictionary = ast.literal_eval(contents)
    file.close()
    return dictionary

def getHis (fileName, target):
    data = readTrainHis(fileName)
    return data[target]

def statisticsCal (datasets):
    modelList = []
    data = []
    for i in range(0 ,len(datasets['fileName'])):
        model = datasets['fileName'][i].split(bas.fileSep)[-1][:-4]
        if model[-1] == '0':
            if model[:-2] not in modelList:
                modelList.append(model[:-2])
                data.append([model[:-2], datasets['accuracy'][i]])
        else:
            idx = modelList.index(model[:-2])
            data[idx].append(datasets['accuracy'][i])
    for i in range(0, len(data)):
        data[i].append(meanCal(data[i][1:]))
        data[i].append(varianceCal(data[i][1:]))
    return data

            


def meanCal(data, dof=0):
    n = len(data)
    return sum(data) / n

def varianceCal(data, dof=0):
    n = len(data)
    mean = sum(data) / n
    return sum((x - mean) ** 2 for x in data) / (n - dof)