import tool.basicTool as bas
import tool.evaluateTool as eva

import tool.learningTool as lrn


historyPath = bas.createFolder(bas.pathWithList(['lib', 'model', 'groundWater', 'history']))
domainList = bas.domainList[0:1]
dataList = bas.dataList[0:1]

for domain in domainList:
    for data in dataList:
        resultPath = bas.createFolder(bas.pathWithList(['datasets', domain, data, 'groundWater']))
        for times in range(0, 1):
            historyPath = historyPath + '_'.join([domain, data, str(times)]) + '.txt'
            X = eva.getHis(historyPath, 'normalize')
            X_norm = lrn.normalize_X(X)
            print(X)
            print(X_norm)