import os
import sys
import numpy as np
import pandas as pd
from osgeo import gdal, gdalconst, ogr, osr


def getImgArr(file):
    return flatArray(readImg(file))

def readImg (file):
    try:
        dataset = gdal.Open(file, gdal.GA_ReadOnly)
        data = dataset.GetRasterBand(1).ReadAsArray()
        dataset = None
        return data
    except Exception:
        sys.exit(1)

def setImg (rangeArr, resultArr):
    returnArr = []
    j = 0
    for i in range(0, len(rangeArr)):
        print(resultArr[j])
        if rangeArr[i] == 0:
            returnArr.append(0)
        else:
            returnArr.append(resultArr[j])
            j = j + 1
    print(np.array(returnArr))
    return np.array(returnArr)

def writeImg (imgArr, refImage, outImage):
    print('Write Img, output: ', outImage)
    dataset = gdal.Open(refImage, gdal.GA_ReadOnly)
    data = dataset.GetRasterBand(1).ReadAsArray()

    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    output = gdal.GetDriverByName(gdalformat).Create(outImage, dataset.RasterXSize, dataset.RasterYSize, 1, datatype, options=['COMPRESS=DEFLATE'])
    output.SetProjection(dataset.GetProjectionRef())
    output.SetGeoTransform(dataset.GetGeoTransform())
    output.GetRasterBand(1).WriteArray(imgArr.astype("float32"))

    dataset = None
    output = None

def setData (rangeArr, targetArr):
    returnArr = []
    for i in range(0, len(rangeArr)):
        if rangeArr[i] == 1:
            if targetArr[i] > 0:
                returnArr.append(targetArr[i])
            else:
                returnArr.append(0)
    return np.array(returnArr)


def flatArray (arr):
    try:
        if arr.ndim == 2:
            flattenArr = []
            row = arr.shape[0]
            col = arr.shape[1]
            for j in range(0, row):
                for i in range(0, col):
                    flattenArr.append(arr[j][i])
            return np.array(flattenArr)
        else:
            print('Check your input array!')
            sys.exit(1)
    except Exception:
        print('Input array must be np.array!')
        sys.exit(1)

def unflattenArr (arr, refArr):
    try:
        if arr.ndim == 1 and refArr.ndim == 2:
            unflattenArr = []
            row = refArr.shape[0]
            col = refArr.shape[1]
            for j in range(0, row):
                unflattenArr.append([])
                for i in range(0, col):
                    unflattenArr[j].append(arr[i + col * j])
            return np.array(unflattenArr)
        else:
            print('Check your input array!')
            sys.exit(1)
    except Exception:
        print('Input array must be np.array!')
        sys.exit(1)

def clipImg (originFile, clipShape, outFile):
    print('Clipping:', originFile)
    originImg = gdal.Open(originFile)
    gdal.Warp(outFile, originImg, **setClipOption(clipShape), dstSRS='EPSG:32651')
    originImg = None
    print('Output:',outFile)

def readFile (fileName):
    try:
        return gdal.Open(fileName, gdal.GA_ReadOnly)
    except Exception:
        sys.exit(1)

def readBand (gdalFile):
    try:
        data = gdalFile.GetRasterBand(1)
        return data
    except Exception:
        sys.exit(1)

def setClipOption (shpFile):
    return {'format': 'GTiff',
            'srcNodata': 0,
            'dstNodata': -32767,
            'xRes': 10,
            'yRes': -10,
            'resampleAlg': 'bilinear',
            'cutlineDSName': shpFile,
            'cropToCutline': True
            }

def shp2tif (inputFile, refFile, outputFile):
    print('Shapefile to tiffile, outputFile: ', outputFile)
    # set file type
    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    # get reference image
    refImg = gdal.Open(refFile, gdal.GA_ReadOnly)
    # get shapefile
    shapeFile = ogr.Open(inputFile)
    shapeFileLayer = shapeFile.GetLayer()
    # print('rasterising')
    # create file and set default
    output = gdal.GetDriverByName(gdalformat).Create(outputFile, refImg.RasterXSize, refImg.RasterYSize, 1, datatype, options=['COMPRESS=DEFLATE'])
    output.SetProjection(refImg.GetProjectionRef())
    output.SetGeoTransform(refImg.GetGeoTransform())
    # write band and no data value
    band = output.GetRasterBand(1)
    band.SetNoDataValue(0)
    gdal.RasterizeLayer(output, [1], shapeFileLayer, burn_values=[1])
    # print('Done.')
    # print('Output file: ', outputFile)
    # Close datasets
    band = None
    output = None
    refImg = None
    shapeFile = None

def csv2shp(csvFile, outputShp):
    if os.path.exists(csvFile):
        # outputShp = dataFolder + 'waterPoint.shp'
        print(csvFile)
        print('Read csv to shapeFile, file name: ', outputShp)
        
        EPSG_code = 32651
        spatialReference = osr.SpatialReference()
        spatialReference.ImportFromEPSG(int(EPSG_code))
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(outputShp)
        layer = shapeData.CreateLayer('layer', spatialReference, ogr.wkbPoint)
        layerDefn = layer.GetLayerDefn()

        layer.CreateField(ogr.FieldDefn('x', ogr.OFTString))
        layer.CreateField(ogr.FieldDefn('y', ogr.OFTString))
        layer.CreateField(ogr.FieldDefn('elev', ogr.OFTString))

        file = pd.read_csv(csvFile)
        for i in range(0, len(file['x'])):
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(file['x'][i]), float(file['y'][i]))
            feature = ogr.Feature(layerDefn)
            feature.SetGeometry(point)
            feature.SetFID(i)
            feature.SetField(feature.GetFieldIndex('x'), file['x'][i])
            feature.SetField(feature.GetFieldIndex('y'), file['y'][i])
            feature.SetField(feature.GetFieldIndex('elev'), file['elev'][i])
            layer.CreateFeature(feature)
        
        shapeData.Destroy()

    else:
        print('Please create elev.csv')