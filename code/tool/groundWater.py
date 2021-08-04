import tool.evaluateTool as eva
import tool.basicTool as bas
import tool.calTool as cal

import struct
import numpy as np
from osgeo import gdal, gdalconst, ogr, osr
from keras.models import load_model


featureList = ['aspect', 'slope', 'TPI', 'curvature']

def predict (domain, modelName):
    print(domain, modelName)
    model = load_model(bas.pathWithList(['lib', 'model', 'groundWater']) + modelName + '.h5')
    history = bas.pathWithList(['lib', 'model', 'groundWater', 'history']) + modelName + '.txt'
    result = bas.createFolder(bas.pathWithList(['datasets', domain, 'groundWater'])) + modelName + '.tif'
    scaler = eva.getHis(history, 'normalize')
    # print(scaler)
    fileList = [bas.pathWithList(['datasets', domain, 'topographic']) + f + '.tif' for f in featureList]
    fileList.append(bas.getDomainFile(domain, 'tif'))
    file = cal.fileOpen(fileList)
    band = cal.rasterBand(file)
    datasetOut = cal.createTmp('groundWater_.tif', file[0])
    for line in range(band[0].YSize):
        tupleData = cal.scanBandData(band, line)
        for i in range(len(tupleData[0])):
            val = 0
            if tupleData[-1][i] == 1:
                idx = featureList.index('aspect')
                a = (tupleData[idx][i] - scaler[1][idx]) / (scaler[0][idx] - scaler[1][idx])
                idx = featureList.index('slope')
                s = (tupleData[idx][i] - scaler[1][idx]) / (scaler[0][idx] - scaler[1][idx])
                idx = featureList.index('TPI')
                t = (tupleData[idx][i] - scaler[1][idx]) / (scaler[0][idx] - scaler[1][idx])
                idx = featureList.index('curvature')
                c = (tupleData[idx][i] - scaler[1][idx]) / (scaler[0][idx] - scaler[1][idx])
                y_predict = model.predict(np.array([[a, s, t, c]]))
                
                val = y_predict[0][0]
            
            if i == 0:
                outputLine = struct.pack('f', val)
            else:
                outputLine = outputLine + struct.pack('f', val)
        datasetOut.GetRasterBand(1).WriteRaster(0, line, band[0].XSize, 1, outputLine,
                                                buf_xsize=band[0].XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    
    gdal.Warp(result, datasetOut, **cal.setClipOption(bas.getDomainFile(domain, 'shp')))
    for b in band:
        b = None
    band = None