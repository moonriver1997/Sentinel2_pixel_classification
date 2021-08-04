import tool.learningTool as lrn
import tool.predictTool as pre
import tool.paramsTool as par
import tool.imageTool as img
import tool.basicTool as bas


target = 'water'
modelPath = bas.path_withList(['other', 'model', target])
modelCate = ['13Bands', 'sunPara', 'dem', 'dem_sunPara', 'hillshade', 'dem_hillshade_sunPara', 'dem_hillshade']
modelList = { '13Bands': [], 'sunPara': [], 'dem': [], 'dem_sunPara': [], 'hillshade': [], 'dem_hillshade_sunPara': [], 'dem_hillshade': []}
optimizerList = ['Adam', 'Nadam', 'SGD', 'RMSprop', 'Adadelta', 'Adagrad']
for model in bas.getDirList(modelPath):

    if model[-2:] == 'h5':
        tmp = model[:-3].split('_')
        if tmp[-3] in optimizerList:
            if 'hillshade' not in tmp and 'dem' not in tmp and 'para' not in tmp:
                modelList['13Bands'].append(model[:-3])
            elif 'hillshade' in tmp and 'dem' not in tmp and 'para' not in tmp:
                modelList['hillshade'].append(model[:-3])
            elif 'hillshade' not in tmp and 'dem' in tmp and 'para' not in tmp:
                modelList['dem'].append(model[:-3])
            elif 'hillshade' not in tmp and 'dem' not in tmp and 'para' in tmp:
                modelList['sunPara'].append(model[:-3])
            elif 'hillshade' in tmp and 'dem' in tmp and 'para' in tmp:
                modelList['dem_hillshade_sunPara'].append(model[:-3])
            elif 'hillshade' not in tmp and 'dem' in tmp and 'para' in tmp:
                modelList['dem_sunPara'].append(model[:-3])

# helperBot = pre.predictHis()

dataList = bas.dataList[0:1]
domain = bas.domainList[2]


domainTif = bas.getDomainFile(domain, 'tif')
domainShp = bas.getDomainFile(domain, 'shp')
# img.shp2tif(domainShp, bas.path_withList(['datasets', domain, '20180327']) + 'B03.tif', domainTif)
domainImg = img.readImg(domainTif)
domainArr = img.flatArray(domainImg)

tmpPredict = bas.path_withList(['other', 'tif']) + 'waterPredict_opt.tif'
for i in range(0, len(dataList)):
    data = dataList[i:i+1]
    print("Domain:", domain, "Data:", data[0])
    resultPath = bas.createFolder(bas.path_withList(['datasets', domain, data[0], target, 'opt']))
    print("File in ", resultPath)
    for category in modelCate:
        print(category)
        if len(modelList[category]) != 0:
            bandList = pre.featureBand(category)
            paraList = pre.featurePara(category)
            X = lrn.build_X(domainArr, domain, data, bandList, paraList)
            X_norm = lrn.normalize_X(X)
            for model in modelList[category]:
                # if helperBot.state == 2:
                modelName = modelPath + model + '.h5'
                result = resultPath + model + '.tif'
                print(result)
                print('model load:', model)
                y_predict = lrn.predict_PixelClassification(modelName, X_norm)
                resultArr = img.unflattenArr(img.setImg(domainArr, y_predict), domainImg)
                img.writeImg(resultArr, domainTif, tmpPredict)
                # helperBot.predictRecord(model, domain, data[0])
                img.clipImg(tmpPredict, domainShp, result)