import tool.learningTool as lrn
import tool.paramsTool as par
import tool.imageTool as img
import tool.basicTool as bas

target = 'water'
modelPath = bas.createFolder(bas.pathWithList(['lib', 'model', 'pixelClassification', target]))
historyPath = bas.createFolder(bas.pathWithList(['lib', 'model', 'pixelClassification', target, 'history']))

time = 'all'
domain = bas.domainList[0]
AreaNum = 1

# ===
if time == 'all':
    dataList = bas.dataList
elif time == 'single':
    dataList = bas.dataList[0:1]
area = str(AreaNum).zfill(2)

bandList = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B11', 'B12', 'B8A', 'hillshade']
# paraList = []
paraList = []
optimizerList = ['Adagrad']
# optimizerList = ['Adam', 'Nadam', 'SGD', 'RMSprop', 'Adadelta', 'Adagrad']
modelName = '_'.join(['', '',domain, area])

if 'dem' in bandList:
    modelName = modelName + '_dem'
if 'hillshade' in bandList:
    modelName = modelName + '_hillshade'
if paraList != []:
    modelName = modelName + '_para'

trainTif = bas.path_withList(['lib', 'domainClip']) + domain + '_' + area + '.tif'
trainImg = img.readImg(trainTif)
trainArr = img.flatArray(trainImg)

data = dataList
if len(data) == len(bas.dataList):
    modelPath = modelPath + 'all' + modelName
    historyPath = historyPath + 'all' + modelName
else:
    modelPath = modelPath + data[0][4:8] + modelName
    historyPath = historyPath + data[0][4:8] + modelName

X_train = lrn.build_X(trainArr, domain, data, bandList, paraList)
y_train = lrn.build_y(trainArr, domain, data, target)
X_train_norm = lrn.normalize_X(X_train)


for opt in optimizerList:
    for neuron in [13]:
        for times in range(2, 3):
            # model = '_'.join([modelPath, str(times)]) + '.h5'
            model = '_'.join([modelPath, opt, str(neuron), str(times)]) + '.h5' 
            print(model)
            score, history = lrn.training_PixelClassification_para(X_train_norm, y_train, X_train_norm, y_train, model, opt, neuron)
            resultDict = {'model': model, 'score': score, 'pixelNum': len(X_train_norm), 'history': history}

            # outFile = '_'.join([historyPath, str(times)]) + '.txt'
            outFile = '_'.join([historyPath, opt, str(neuron), str(times)]) + '.txt'
            with open(outFile, 'w') as filehandle:
                for listitem in [resultDict]:
                    filehandle.write('%s\n' % listitem)