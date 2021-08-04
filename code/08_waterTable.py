import tool.waterTool as wat
import tool.basicTool as bas
import tool.imageTool as img

domainList = bas.domainList[0:1]
# domainList = bas.domainList[1:2]
# domainList = bas.domainList[2:]
dataList = bas.dataList[1:2]

target = 'water'

for data in dataList:
    for domain in domainList:
        print('Data:', data, ", Domain:", domain)

        ## get water elev
        dataFolder = bas.createFolder(bas.pathWithList(['datasets', domain, data, target, 'waterTable']))
        
        # predict = ''
        # csvFile = dataFolder + 'waterElev' + predict + '.csv'
        # waterName = target
        # waterFile = bas.pathWithList(['datasets', domain, data]) + waterName + '.tif'

        # # wat.waterElev(domain, waterFile, csvFile)
        # # img.csv2shp(csvFile, dataFolder + 'waterPoint' + predict + '.shp')

        # tmpWater = dataFolder + target + 'High.tif'
        # domainShp = bas.getDomainFile(domain, 'shp')
        # img.clipImg(tmpWater, domainShp, dataFolder + target + 'Elev.tif')
        
        predict = '_predict'
        # csvFile = dataFolder + 'waterElev' + predict + '.csv'
        # waterName = 'all__51N_Center_06_dem_hillshade_para_1'
        # waterFile = bas.pathWithList(['datasets', domain, data, target]) + waterName + '.tif'
        
        
        # wat.waterElev(domain, waterFile, csvFile)
        # img.csv2shp(csvFile, dataFolder + 'waterPoint' + predict + '.shp')



        # tmpWater = dataFolder + target + 'High' + predict + '.tif'
        # domainShp = bas.getDomainFile(domain, 'shp')
        # img.clipImg(tmpWater, domainShp, dataFolder + target + 'Elev' + predict + '.tif')
        tmpWater = dataFolder + target + 'High' + predict + '_adj_.tif'
        domainShp = bas.getDomainFile(domain, 'shp')
        img.clipImg(tmpWater, domainShp, dataFolder + target + 'Elev' + predict + '_adj.tif')