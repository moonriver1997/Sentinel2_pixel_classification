import tool.basicTool as bas
import tool.imageTool as img
import tool.learningTool as lrn



modelPath = bas.createFolder(bas.pathWithList(['lib', 'model', 'groundWater']))
historyPath = bas.createFolder(bas.pathWithList(['lib', 'model', 'groundWater', 'history']))

featureList = ['aspect', 'slope', 'TPI', 'curvature']
paraList = []
domainList = bas.domainList
dataList = bas.dataList


for domain in domainList:
    for data in dataList:
        trainTif = bas.pathWithList(['datasets', domain, data]) + 'waterPredict.tif'
        trainImg = img.readImg(trainTif)
        trainArr = img.flatArray(trainImg)
        X_train = lrn.build_X(trainArr, domain, [data], featureList, paraList)
        y_train = lrn.build_y(trainArr, domain, [data], 'dem')
        X_train_norm, normMax, normMin = lrn.normalize_GroundWater(X_train)
        # y_train_norm = lrn.normalize_y(y_train)
        for times in range(0, 1):
            model = modelPath + '_'.join([domain, data, str(times)]) + '.h5'
            # score, history = lrn.training_GroundWater(X_train_norm, y_train_norm, X_train_norm, y_train_norm, model)
            score, history = lrn.training_GroundWater(X_train_norm, y_train, X_train_norm, y_train, model)
            resultDict = {'model': model, 'score': score, 'normalize': [normMax, normMin],'pixelNum': len(X_train_norm), 'history': history}

            outFile =  historyPath + '_'.join([domain, data, str(times)]) + '.txt'
            with open(outFile, 'w') as filehandle:
                for listitem in [resultDict]:
                    filehandle.write('%s\n' % listitem)
            
