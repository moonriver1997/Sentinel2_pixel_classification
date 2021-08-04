import tool.dbTool as dbs
import tool.basicTool as bas
import tool.evaluateTool as eva


## draw model training history
target = 'water'
hisPath = bas.pathWithList(['lib', 'model', 'pixelClassification', target, 'history'])
hisList = bas.getDirList(hisPath)

result = []

for file in hisList:
    if file[-4:] == '.txt':
        modelName, epochNum, pixelNum, score = eva.processHistoryData(hisPath, file)
        result.append([modelName, epochNum, pixelNum, score[1], score[0]])

dbs.writeExcel(result, ['model', 'Epoch', 'pixelNum', 'accuracy', 'loss'], bas.pathWithList(['lib', 'database']) + 'modelResult.xlsx')