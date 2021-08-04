import tool.dbTool as dbs
import tool.basicTool as bas
import tool.evaluateTool as eva

dataList = bas.dataList
domainList = bas.domainList
target = 'water'

# '''
## accuracy cal
for data in dataList:
    for domain in domainList:
        result = []
        filePath = bas.pathWithList(['datasets', domain, data, target])
        targetPath = bas.pathWithList(['datasets', domain, data]) + target + '.tif'
        domainFile = bas.getDomainFile(domain, 'tif')
        for img in bas.getDirList(filePath):
            if img[-4:] == '.tif': 
                resultPath = filePath + img
                acc, errPix, allPix = eva.evaluate(targetPath, resultPath, domainFile)
                result.append([resultPath, 1-acc, errPix, allPix])
        excelPath = bas.pathWithList(['lib', 'accuracyCal']) + '_'.join([data, domain, target + '.xlsx'])
        dbs.writeExcel(result, ['fileName', 'accuracy', 'errPix', 'allPix'], excelPath)
# '''
## variance cal
for data in dataList:
    statisticData = []
    for filePath in ['_'.join(['', d, target]) + '.xlsx' for d in domainList]:
        statisticData = eva.statisticsCal(dbs.readExcel(bas.pathWithList(['result']) + data + filePath))
        col = ['model','train_1', 'train_2', 'train_3', 'mean', 'variance']
        dbs.writeExcel(statisticData, col, bas.pathWithList(['lib', 'accuracyCal']) + data + filePath)