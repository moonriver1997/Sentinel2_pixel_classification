# from keras.models import load_model
import tool.basicTool as bas
import tool.dbTool as dbs

import time

# # ===
# def predict (modelName, X):
#     print('Predict')
#     model = load_model(modelName)
#     return model.predict_classes(X)

def featureBand(modelCate):
    tmpBand = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B11', 'B12', 'B8A']
    if modelCate == 'dem' or modelCate == 'dem_sunPara':
        tmpBand.append('dem')
    elif modelCate == 'hillshade'or modelCate == 'hillshade_sunPara':
        tmpBand.append('hillshade')
    elif modelCate == 'dem_hillshade' or modelCate == 'dem_hillshade_sunPara':
        tmpBand.append('dem')
        tmpBand.append('hillshade')
    elif  modelCate != '13Bands' and modelCate != 'sunPara':
        print('Error params')
    return tmpBand

def featurePara(modelCate):
    if 'sunPara' in modelCate.split('_'):
        return ['altitude', 'azimuth']
    return []


class predictHis ():
    def __init__(self):
        self.botState = {0: 'preparing', 1: 'checking', 2: 'predicting', -1: 'error'}
        self.state = 0
        self.historyPath = bas.path_withList(['other', 'database']) + 'predictHis.xlsx'
    
    def predicting(self, modelName, domainName, dataName):
        self.state = 1
        self.his = dbs.readExcel(self.historyPath)
        hisList = []
        for history in self.his.values.tolist():
            hisList.append([history[1], history[2], history[3]])
        # print(hisList)
        # modelList = self.his['model'].tolist()
        # domainList = self.his['domain'].tolist()
        # dataList = self.his['data'].tolist()
        # if modelName not in modelList or domainName not in domainList or int(dataName) not in dataList:
        if [modelName, domainName, int(dataName)] not in hisList:
            self.state = 2
        else:
            self.state = 0

    
    def predictRecord(self, modelName, domain, data):
        dataset = self.his.values.tolist()
        dataset.append([time.strftime("%Y%m%d %H:%M:%S"), modelName, domain, data])
        columns = ['time', 'model', 'domain', 'data']
        dbs.writeExcel(dataset, columns, self.historyPath)
        self.state = 0
