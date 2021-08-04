import tool.basicTool as bas
import tool.imageTool as img
import tool.calTool as cal

import struct
import pandas as pd
from osgeo import gdal, gdalconst, ogr, osr

def channel (domain):
    dataFolder = bas.pathWithList(['datasets', domain, 'topographic'])
    waterFile = dataFolder + 'Number of cells that drain through each cell.tif'
    waterData = gdal.Open(waterFile, gdal.GA_ReadOnly)
    waterBand = waterData.GetRasterBand(1)

    pathOut = bas.pathWithList(['lib', 'tmp']) + 'channel.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, waterData.RasterXSize, waterData.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(waterData.GetGeoTransform())
    datasetOut.SetProjection(waterData.GetProjection())

    numLines = waterBand.YSize
    for line in range(numLines):
        scanlineWater = waterBand.ReadRaster(0, line, waterBand.XSize, 1, waterBand.XSize, 1, gdal.GDT_Float32)
        tupleWater = struct.unpack('f' * waterBand.XSize, scanlineWater)

        for i in range(len(tupleWater)):
            val = 0
            if tupleWater[i] < -20:
                val = 1

            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)

        datasetOut.GetRasterBand(1).WriteRaster(0, line, waterBand.XSize, 1, outputLine,
                                                buf_xsize=waterBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    gdal.Warp(dataFolder+'channel.tif', datasetOut, **cal.setClipOption(bas.getDomainFile(domain, 'shp')))
    waterBand = None

def waterTmp (dataFolder, domain):
    waterFile = dataFolder + 'waterVol.tif'
    waterData = gdal.Open(waterFile, gdal.GA_ReadOnly)
    waterBand = waterData.GetRasterBand(1)
    domainFile = gdal.Open(bas.getDomainFile(domain, 'tif'), gdal.GA_ReadOnly)
    domainBand = domainFile.GetRasterBand(1)

    pathOut = bas.pathWithList(['lib', 'tmp']) + 'waterTmp.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, waterData.RasterXSize, waterData.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(waterData.GetGeoTransform())
    datasetOut.SetProjection(waterData.GetProjection())

    numLines = waterBand.YSize
    area = 0
    for line in range(numLines):
        scanlineWater = waterBand.ReadRaster(0, line, waterBand.XSize, 1, waterBand.XSize, 1, gdal.GDT_Float32)
        tupleWater = struct.unpack('f' * waterBand.XSize, scanlineWater)

        scanlineDomain = domainBand.ReadRaster(0, line, domainBand.XSize, 1, domainBand.XSize, 1, gdal.GDT_Float32)
        tupleDomain = struct.unpack('f' * domainBand.XSize, scanlineDomain)
        for i in range(len(tupleWater)):
            val = 0
            if tupleDomain[i] > 0:
                if tupleWater[i] > 0:
                    val = 1
                    area = area + 1

            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)

        datasetOut.GetRasterBand(1).WriteRaster(0, line, waterBand.XSize, 1, outputLine,
                                                buf_xsize=waterBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    gdal.Warp(dataFolder+'waterTmp.tif', datasetOut, **cal.setClipOption(bas.getDomainFile(domain, 'shp')))
    waterBand = None
    domainBand = None
    return area * 20 * 20

def waterArea (dataFolder, domain):
    waterFile = dataFolder + 'waterPredict.tif'
    waterData = gdal.Open(waterFile, gdal.GA_ReadOnly)
    waterBand = waterData.GetRasterBand(1)
    domainFileName = bas.pathWithList(['lib', 'domainClip']) + domain
    domainFile = gdal.Open(domainFileName + '.tif', gdal.GA_ReadOnly)
    domainBand = domainFile.GetRasterBand(1)

    # pathOut = bas.pathWithList(['lib', 'tmp']) + 'waterArea.tif'
    # driver = gdal.GetDriverByName("GTiff")
    # datasetOut = driver.Create(pathOut, waterData.RasterXSize, waterData.RasterYSize, 1, gdal.GDT_Float32)
    # datasetOut.SetGeoTransform(waterData.GetGeoTransform())
    # datasetOut.SetProjection(waterData.GetProjection())

    numLines = waterBand.YSize
    area = 0
    for line in range(numLines):
        scanlineWater = waterBand.ReadRaster(0, line, waterBand.XSize, 1, waterBand.XSize, 1, gdal.GDT_Float32)
        tupleWater = struct.unpack('f' * waterBand.XSize, scanlineWater)

        scanlineDomain = domainBand.ReadRaster(0, line, domainBand.XSize, 1, domainBand.XSize, 1, gdal.GDT_Float32)
        tupleDomain = struct.unpack('f' * domainBand.XSize, scanlineDomain)
        for i in range(len(tupleWater)):
            # val = 0
            if tupleDomain[i] > 0:
                if tupleWater[i] > 0:
                    area = area + 1
                    # val = 1
            
    #         if i == 0:
    #             outputLine = struct.pack('f', val)
    #         else:
    #             outputLine = outputLine + struct.pack('f', val)

    #     datasetOut.GetRasterBand(1).WriteRaster(0, line, waterBand.XSize, 1, outputLine,
    #                                             buf_xsize=waterBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    # gdal.Warp(dataFolder+'waterArea.tif', datasetOut, **cal.setClipOption(domainFileName + '.shp'))
    waterBand = None
    domainBand = None
    return area * 20 * 20

def waterVol (dataFolder, domain):
    waterFile = dataFolder + 'waterTable_predict_adj_.tif'
    # waterFile = dataFolder + 'waterTable_predict_adj.tif'
    # waterFile = dataFolder + 'waterTable.tif'
    waterData = gdal.Open(waterFile, gdal.GA_ReadOnly)
    waterBand = waterData.GetRasterBand(1)
    domainFile = gdal.Open(bas.getDomainFile(domain, 'tif'), gdal.GA_ReadOnly)
    domainBand = domainFile.GetRasterBand(1)

    pathOut = bas.pathWithList(['lib', 'tmp']) + 'waterVol.tif'
    # pathOut = bas.pathWithList(['lib', 'tmp']) + 'waterVol_.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, waterData.RasterXSize, waterData.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(waterData.GetGeoTransform())
    datasetOut.SetProjection(waterData.GetProjection())

    numLines = waterBand.YSize
    vol = 0.0
    for line in range(numLines):
        scanlineWater = waterBand.ReadRaster(0, line, waterBand.XSize, 1, waterBand.XSize, 1, gdal.GDT_Float32)
        tupleWater = struct.unpack('f' * waterBand.XSize, scanlineWater)

        scanlineDomain = domainBand.ReadRaster(0, line, domainBand.XSize, 1, domainBand.XSize, 1, gdal.GDT_Float32)
        tupleDomain = struct.unpack('f' * domainBand.XSize, scanlineDomain)
        for i in range(len(tupleWater)):
            val = 0
            tmpVol = 0
            if tupleDomain[i] > 0:
                if tupleWater[i] > -50 and tupleWater[i] < 0:
                    val = 1
                    tmpVol = 50 + tupleWater[i]
                elif tupleWater[i] > 0: 
                    val = 2
                    tmpVol = 50
            
                if val != 0:
                    # print(tmpVol)
                    vol = tmpVol + vol

            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)

        datasetOut.GetRasterBand(1).WriteRaster(0, line, waterBand.XSize, 1, outputLine,
                                                buf_xsize=waterBand.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    # gdal.Warp(dataFolder+'waterVol.tif', datasetOut, **cal.setClipOption(bas.getDomainFile(domain, 'shp')))
    gdal.Warp(dataFolder+'waterVol_.tif', datasetOut, **cal.setClipOption(bas.getDomainFile(domain, 'shp')))
    waterBand = None
    domainBand = None
    return vol * 20 * 20 * 0.08

def waterElev (domain, waterFile, csvOut):

    demFile = bas.getDomainFile(domain, 'dem')
    dem = gdal.Open(demFile, gdal.GA_ReadOnly)
    TL_x, x_res, _, TL_y, _, y_res = dem.GetGeoTransform()
    demBand = dem.GetRasterBand(1)

    print(waterFile)
    water = gdal.Open(waterFile, gdal.GA_ReadOnly)
    waterBand = water.GetRasterBand(1)

    pathOut = bas.pathWithList(['lib', 'tmp']) + 'waterElev.tif'
    driver = gdal.GetDriverByName("GTiff")
    datasetOut = driver.Create(pathOut, dem.RasterXSize, dem.RasterYSize, 1, gdal.GDT_Float32)
    datasetOut.SetGeoTransform(dem.GetGeoTransform())
    datasetOut.SetProjection(dem.GetProjection())


    elev = []
    lineNum = demBand.YSize
    # print(demBand.YSize)
    # print(waterBand.YSize)
    for line in range(0,lineNum):
        
        scanlineWater = waterBand.ReadRaster(0, line, waterBand.XSize, 1, waterBand.XSize, 1, gdal.GDT_Float32)
        tupleWater = struct.unpack('f' * waterBand.XSize, scanlineWater)

        scanlineDem = demBand.ReadRaster(0, line, demBand.XSize, 1, demBand.XSize, 1, gdal.GDT_Float32)
        tupleDem = struct.unpack('f' * demBand.XSize, scanlineDem)

        for i in range(len(tupleDem)):
            # calculation
            val = 0
            if tupleDem[i] > 0:
                if tupleWater[i] == 1:
                    x = i * x_res + TL_x
                    y = line * y_res + TL_y
                    elev.append([x, y, tupleDem[i]])
    
    df = pd.DataFrame(elev, columns=['x', 'y', 'elev'])
    df.to_csv(csvOut, index=None)

    datasetOut = None
    waterBand = None
    demBand = None