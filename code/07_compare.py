import tool.basicTool as bas
import tool.imageTool as img
import tool.evaluateTool as eva

dataList = bas.dataList[0:1]
domainList = bas.domainList[0:1]
target = 'water'
AreaNum = 1



for data in dataList:
    for domain in domainList:
        print(data, domain)
        # domainFile = bas.getDomainFile(domain, 'tif')
        domainFile = bas.pathWithList(['lib', 'domainClip']) + domain + '_' + str(AreaNum).zfill(2) + '.tif'
        filePath = bas.pathWithList(['datasets', domain, data])
        targetPath = filePath + target + '.tif'
        resultPath = filePath + 'ndwi.tif'
        acc, errPix, allPix = eva.evaluate(targetPath, resultPath, domainFile)
        print('NDWI:', 1-acc, errPix, allPix)
        resultPath = filePath + 'hdwi.tif'
        acc, errPix, allPix = eva.evaluate(targetPath, resultPath, domainFile)
        print('HDWI:', 1-acc, errPix, allPix)