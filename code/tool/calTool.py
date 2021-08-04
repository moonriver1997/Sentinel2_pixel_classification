import os
import struct
from osgeo import gdal, gdalconst, ogr, osr

import tool.basicTool as bas

def evaluate(filePath, trueFile, dataFile, domainFile):
    trueData = gdal.Open(filePath+trueFile, gdal.GA_ReadOnly)
    trueBand = trueData.GetRasterBand(1)
    data = gdal.Open(filePath+dataFile, gdal.GA_ReadOnly)
    dataBand = data.GetRasterBand(1)
    domain = gdal.Open(domainFile + '.tif', gdal.GA_ReadOnly)
    # domain = gdal.Open(filePath + 'noCloud.tif', gdal.GA_ReadOnly)
    domainBand = domain.GetRasterBand(1)

    # pathOut = 'tmp\\tmp.tif'
    # driver = gdal.GetDriverByName("GTiff")
    # datasetOut = driver.Create(pathOut, data.RasterXSize, data.RasterYSize, 1, gdal.GDT_Float32)
    # datasetOut.SetGeoTransform(data.GetGeoTransform())
    # datasetOut.SetProjection(data.GetProjection())

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
        
        #     if i == 0:
        #         outputLine = struct.pack('f', val)
        #     else:
        #         outputLine = outputLine + struct.pack('f', val)
        # datasetOut.GetRasterBand(1).WriteRaster(0, line, dataBand.XSize, 1, outputLine,
                                                # buf_xsize=dataBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    # gdal.Warp(filePath + 'tmp.tif', datasetOut, **setClipOption(domainFile + '.shp'))
    print(dataFile, errPix, allPix)
    trueBand = None
    dataBand = None

    return errPix/allPix, errPix, allPix


def warpSentinel (fileList, dataPath, domainShp, bandList):
    print('Sentinel warpping')
    typeFile = '.jp2'
    print('Reproject')
    bandRef = 'B03'
    dstFileList = [f+bandRef+typeFile for f in fileList]
    vrtOption = gdal.BuildVRTOptions(VRTNodata=-32767, hideNodata=True)
    gdal.BuildVRT(bas.pathWithList(['lib', 'tmp']) + 'tmpRefMergeImg.vrt', dstFileList, options=vrtOption)
    dstImg = gdal.Open(bas.pathWithList(['lib', 'tmp']) + 'tmpRefMergeImg.vrt')
    transImg = dstImg.GetGeoTransform()
    minX = transImg[0]
    maxY = transImg[3]
    maxX = minX + transImg[1]*dstImg.RasterXSize
    minY = maxY + transImg[5]*dstImg.RasterYSize
    warpOption = {'format': 'MEM',
                'resampleAlg': 'bilinear',
                'xRes': 10,
                'yRes': -10,
                'outputBounds': [minX, minY, maxX, maxY],
                'outputBoundsSRS': 'EPSG:32651'
                }
    for band in bandList:
        print('Processing band:', band)
        srcFileList = [f+band+typeFile for f in fileList]
        gdal.BuildVRT(bas.pathWithList(['lib', 'tmp']) + 'tmpSrcMergeImg.vrt', srcFileList, options=vrtOption)
        srcImg = gdal.Open(bas.pathWithList(['lib', 'tmp']) + 'tmpSrcMergeImg.vrt')
        tmpImg = gdal.Warp('', srcImg, **warpOption)
        warpImg = gdal.Warp(dataPath+band+'.tif', tmpImg, **setClipOption(domainShp))
        srcImg = None
        tmpImg = None
        warpImg = None

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

def calRGB (dataPath, shapeFile):
    print('Get RGB image: ', dataPath)
    # 1: red-B04, 2: green-B03, 3: blue-B02
    fileType = '.tif'
    rgbKey = {
        'red': 'B04' + fileType,
        'green': 'B03' + fileType,
        'blue': 'B02' + fileType,
    }
    dataset = gdal.Open(dataPath+'B02' + fileType, gdal.GA_ReadOnly)
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(bas.pathWithList(['lib', 'tmp']) + 'rgb' + fileType, dataset.RasterXSize, dataset.RasterYSize, 3, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(dataset.GetGeoTransform())
    datasetOut.SetProjection(dataset.GetProjection())
    dataset = None
    i = 1
    for tif in rgbKey:
        dataset = gdal.Open(dataPath + rgbKey[tif], gdal.GA_ReadOnly)
        band = dataset.GetRasterBand(1).ReadAsArray()
        datasetOut.GetRasterBand(i).WriteArray(band)
        i = i + 1
        dataset = None
    outputFile = dataPath + 'rgb' + fileType
    gdal.Warp(outputFile, datasetOut, **setClipOption(shapeFile))
    datasetOut = None

def calHillshade (demFile, altitude, azimuth, outputFile):
    # gdaldem hillshade E:/Academic/master/domain/Center_51N_dem.tif E:/Academic/master/tmp/hillshade.tif -of GTiff -b 1 -z 1.0 -s 1.0 -az 156.55 -alt 40.36
    option = ' -of GTiff -b 1 -z 1.0 -s 1.0 -az ' + str(azimuth) +' -alt ' + str(altitude)
    command = 'gdaldem hillshade ' + demFile + ' ' + outputFile + option
    os.system(command)

def calTopoPara (domain, topo):
    print('Domain:', domain, 'analysis:', topo)
    demFile = bas.getDomainFile(domain, 'dem')
    outputFile = bas.pathWithList(['datasets', domain, 'topographic']) + topo + '.tif'
    if topo == 'aspect':
        # gdaldem aspect E:/Academic/groundWaterAnalysisBySentinel2/datasets/51N_Center/51N_Center_dem.tif E:/Academic/groundWaterAnalysisBySentinel2/datasets/51N_Center/topographic/aspect.tif -of GTiff -b 1
        option = ' -of GTiff -b 1'
    elif topo == 'slope':
        # gdaldem slope E:/Academic/groundWaterAnalysisBySentinel2/datasets/51N_Center/51N_Center_dem.tif E:/Academic/groundWaterAnalysisBySentinel2/datasets/51N_Center/topographic/slop.tif -of GTiff -b 1 -s 1.0
        option = ' -of GTiff -b 1 -s 1.0'
    command = 'gdaldem ' + topo + ' ' + demFile + ' ' + outputFile + option
    os.system(command)

def calTwoBand (dataFolder, shapeFile, frontFile, backFile, outputFile, calType):
    print("Calculating (a - b) / (a + b), with a = ", frontFile , 'b = ', backFile)
    fileType = '.tif'
    front = gdal.Open(dataFolder + frontFile + fileType, gdal.GA_ReadOnly)
    frontBand = front.GetRasterBand(1)
    back = gdal.Open(dataFolder + backFile + fileType, gdal.GA_ReadOnly)
    backBand = back.GetRasterBand(1)

    pathOut = bas.pathWithList(['lib', 'tmp']) + 'twoBandCal.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, front.RasterXSize, front.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(front.GetGeoTransform())
    datasetOut.SetProjection(front.GetProjection())

    lineNum = frontBand.YSize
    for line in range(0,lineNum):
        scanlineFront = frontBand.ReadRaster(0, line, frontBand.XSize, 1, frontBand.XSize, 1, gdal.GDT_Float32)
        tupleFront = struct.unpack('f' * frontBand.XSize, scanlineFront)
        scanlineBack = backBand.ReadRaster(0, line, backBand.XSize, 1, backBand.XSize, 1, gdal.GDT_Float32)
        tupleBack = struct.unpack('f' * backBand.XSize, scanlineBack)
        for i in range(len(tupleFront)):
            upper = tupleFront[i] - tupleBack[i]
            lower = tupleFront[i] + tupleBack[i]
            # calculation
            if lower == 0:
                val = 0
            else:
                val = upper / lower
                if calType[0] == 'class':
                    if val > calType[1] :
                        val = 1
                    else:
                        val = 0

            # set data
            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)
        datasetOut.GetRasterBand(1).WriteRaster(0, line, frontBand.XSize, 1, outputLine,
                                                buf_xsize=frontBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    print("File output: ", dataFolder+outputFile)
    gdal.Warp(dataFolder+outputFile, datasetOut, **setClipOption(shapeFile))
    datasetOut = None
    upperBand = None
    lowerBand = None

def calHDWI (dataFolder, outputFile, calType, shapeFile):
    print('Calculating hdwi value, output: ', outputFile)
    # print('Load band...')
    red = gdal.Open(dataFolder + 'B04.tif', gdal.GA_ReadOnly)
    nirA = gdal.Open(dataFolder + 'B05.tif', gdal.GA_ReadOnly)
    nirB = gdal.Open(dataFolder + 'B06.tif', gdal.GA_ReadOnly)
    nirC = gdal.Open(dataFolder + 'B07.tif', gdal.GA_ReadOnly)
    nir = gdal.Open(dataFolder + 'B08.tif', gdal.GA_ReadOnly)
    redBand = red.GetRasterBand(1)
    nirBand = nir.GetRasterBand(1)
    nirABand = nir.GetRasterBand(1)
    nirBBand = nir.GetRasterBand(1)
    nirCBand = nir.GetRasterBand(1)

    # print('Set output...')
    pathOut = bas.pathWithList(['lib', 'tmp']) + 'hdwi.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, red.RasterXSize, red.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(red.GetGeoTransform())
    datasetOut.SetProjection(red.GetProjection())

    returnVal = [-100000, 100000]
    # print('Calculating')
    numLines = redBand.YSize
    for line in range(numLines):
        scanlineRed = redBand.ReadRaster(0, line, redBand.XSize, 1, redBand.XSize, 1, gdal.GDT_Float32)
        tupleRed = struct.unpack('f' * redBand.XSize, scanlineRed)
        scanlineNir = nirBand.ReadRaster(0, line, nirBand.XSize, 1, nirBand.XSize, 1, gdal.GDT_Float32)
        tupleNir = struct.unpack('f' * nirBand.XSize, scanlineNir)
        scanlineNirA = nirABand.ReadRaster(0, line, nirABand.XSize, 1, nirABand.XSize, 1, gdal.GDT_Float32)
        tupleNirA = struct.unpack('f' * nirABand.XSize, scanlineNirA)
        scanlineNirB = nirBBand.ReadRaster(0, line, nirBBand.XSize, 1, nirBBand.XSize, 1, gdal.GDT_Float32)
        tupleNirB = struct.unpack('f' * nirBBand.XSize, scanlineNirB)
        scanlineNirC = nirCBand.ReadRaster(0, line, nirCBand.XSize, 1, nirCBand.XSize, 1, gdal.GDT_Float32)
        tupleNirC = struct.unpack('f' * nirCBand.XSize, scanlineNirC)
        for i in range(len(tupleRed)):
            hdwiLower = (tupleRed[i]*31 + tupleNirA[i]*5) + (tupleNir[i]*12 + tupleNirA[i]*15 + scanlineNirB[i]*20 + tupleNirC[i]*70)
            hdwiUpper = (tupleRed[i]*31 + tupleNirA[i]*5) - (tupleNir[i]*12 + tupleNirA[i]*15 + scanlineNirB[i]*20 + tupleNirC[i]*70)
            hdwi = 0
            if hdwiLower == 0:
                hdwi = 0
            else:
                hdwi = hdwiUpper/hdwiLower
                if calType[0] == 'class':
                    if hdwi > calType[1] :
                        hdwi = 1
                    else:
                        hdwi = 0
            
            # max
            if returnVal[0] < hdwi:
                returnVal[0] = hdwi
            # min
            if returnVal[1] > hdwi:
                returnVal[1] = hdwi

            if i == 0:
                outputLine = struct.pack('f', hdwi)
            else:
                outputLine = outputLine + struct.pack('f', hdwi)
        datasetOut.GetRasterBand(1).WriteRaster(0, line, redBand.XSize, 1, outputLine,
                                                buf_xsize=redBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    # print("END Calculation")
    gdal.Warp(outputFile, datasetOut, **setClipOption(shapeFile))
    datasetOut = None
    greenBand = None
    nirBand = None
    nirABand = None
    nirBBand = None
    nirCBand = None
    return returnVal

def calTmpTrueWater (dataFolder, shapeFile):
    print('Calculate true water')
    outFile = 'tmpWater'
    fileList = ['ndwi', 'SCL']
    file = fileOpen([dataFolder + f + '.tif' for f in fileList])
    band = rasterBand(file)
    datasetOut = createTmp(outFile, file[0])
    for line in range(band[0].YSize):
        # for line in range(2):
        tupleData = scanBandData(band, line)
        for i in range(len(tupleData[0])):
            n = tupleData[fileList.index('ndwi')][i] + 0.05
            c = tupleData[fileList.index('SCL')][i]

            val = 0
            if c < 8.5 or c > 9.5:
                if n > 0:
                    val = 1


            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)
        datasetOut.GetRasterBand(1).WriteRaster(0, line, band[0].XSize, 1, outputLine,
                                                buf_xsize=band[0].XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    gdal.Warp(dataFolder + outFile + '.tif', datasetOut, **setClipOption(shapeFile))
    print('path out',dataFolder)
    print('tmpwater.tif is created, please adjust water pixel to water.tif')
    for b in band:
        b = None
    band = None

def waterAlter (dataFolder, shapeFile):
    print('Calculate true water')
    outFile = 'water'
    fileList = ['tmpWater', 'noWater']
    file = fileOpen([dataFolder + f + '.tif' for f in fileList])
    band = rasterBand(file)
    datasetOut = createTmp(outFile, file[0])
    for line in range(band[0].YSize):
        # for line in range(2):
        tupleData = scanBandData(band, line)
        for i in range(len(tupleData[0])):
            n = tupleData[fileList.index('tmpWater')][i]
            c = tupleData[fileList.index('noWater')][i]

            val = 0
            if n > 0.5 and c < 0.5:
                val = 1


            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)
        datasetOut.GetRasterBand(1).WriteRaster(0, line, band[0].XSize, 1, outputLine,
                                                buf_xsize=band[0].XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    gdal.Warp(dataFolder + outFile + '.tif', datasetOut, **setClipOption(shapeFile))
    print('path out',dataFolder)
    for b in band:
        b = None
    band = None


# ===== gdal tool
def scanBandData (dataList, line):
    scanline = []
    tupleData = []
    for data in dataList:
        idx = len(scanline)
        scanline.append(data.ReadRaster(0, line, data.XSize, 1, data.XSize, 1, gdal.GDT_Float32))
        tupleData.append(struct.unpack('f' * data.XSize, scanline[idx]))
    return tupleData

def createTmp (fileName, refFile):
    pathOut = bas.pathWithList(['lib', 'tmp']) + fileName + '.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, refFile.RasterXSize, refFile.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(refFile.GetGeoTransform())
    datasetOut.SetProjection(refFile.GetProjection())
    return datasetOut

def rasterBand (fileList):
    dataList = []
    for file in fileList:
        dataList.append(file.GetRasterBand(1))
    return dataList

def fileOpen (fileNameList):
    fileList = []
    for fileName in fileNameList:
        fileList.append(gdal.Open(fileName, gdal.GA_ReadOnly))
    return fileList

def defaultBand ():
    return ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B11', 'B12', 'B8A', 'AOT', 'SCL', 'TCI', 'WVP']

