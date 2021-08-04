import tool.learningTool as lrn
import tool.predictTool as pre
import tool.paramsTool as par
import tool.imageTool as img
import tool.basicTool as bas

target = 'water'
modelPath = bas.pathWithList(['lib', 'model', 'pixelClassification', target])
modelList = []
for model in bas.getDirList(modelPath):
    if model[-2:] == 'h5':
        tmp = model[:-3].split('_')
        if 'hillshade' in tmp and 'dem' in tmp and 'para' not in tmp:
            modelList.append(model[:-3])

print(modelList)

helperBot = pre.predictHis()

# dataList = bas.dataList[0:1]
dataList = bas.dataList[1:]
domainList = bas.domainList

category = 'dem_hillshade'
bandList = pre.featureBand(category)
paraList = pre.featurePara(category)

tmpPredict = bas.pathWithList(['lib', 'tmp']) + 'waterPredict.tif'

for domain in domainList:
    domainTif = bas.getDomainFile(domain, 'tif')
    domainShp = bas.getDomainFile(domain, 'shp')
    domainImg = img.readImg(domainTif)
    domainArr = img.flatArray(domainImg)

    for i in range(0, len(dataList)):
        data = dataList[i:i+1]
        print('Domain:', domain, ' ; Data:', data[0])
        resultPath = bas.createFolder(bas.pathWithList(['datasets', domain, data[0], target]))
        X = lrn.build_X(domainArr, domain, data, bandList, paraList)
        X_norm = lrn.normalize_X(X)
        for model in modelList:
            helperBot.predicting(model, domain, data[0])
            if helperBot.state == 2:
                modelName = modelPath + model + '.h5'
                result = resultPath + model + '.tif'
                print(result)
                print('model load:', model)
                y_predict = lrn.predict_PixelClassification(modelName, X_norm)
                resultArr = img.unflattenArr(img.setImg(domainArr, y_predict), domainImg)
                img.writeImg(resultArr, domainTif, tmpPredict)
                helperBot.predictRecord(model, domain, data[0])
                img.clipImg(tmpPredict, domainShp, result)