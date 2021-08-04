import tool.calTool as cal
import tool.basicTool as bas
import tool.imageTool as img
import tool.paramsTool as par

domainList = bas.domainList
dataList = bas.dataList

bandList = cal.defaultBand()


for data in dataList:
    jp2Path = bas.pathWithList(['lib', 'sentinel','raw', data+'B', 'warp'])
    if bas.checkDir(jp2Path):
        sensingTime = bas.getDirList(jp2Path)[0].split('_')[1]
        ## sun parameter
        altitude, azimuth = par.getSunPara(sensingTime, bas.lat, bas.lon)
        for domain in domainList:
            # print('Data processing >>> domain:', domain, 'time:', data)
            ## create data folder
            # bas.createFolder(tifPath)
            domainShp = bas.getDomainFile(domain, 'shp')
            domainDem = bas.getDomainFile(domain, 'dem')
            ## topographic
            if data == dataList[0]:
                cal.calTopoPara(domain, 'slope')
                cal.calTopoPara(domain, 'aspect')
            tifPath = bas.pathWithList(['datasets', domain, data])
            ## calculate hillshade
            # cal.calHillshade(domainDem, altitude, azimuth, tifPath + 'hillshade.tif')
            ## Warp sentinel file
            fileList = [jp2Path + tile + '_' + sensingTime + '_' for tile in bas.tileList]
            # cal.warpSentinel(fileList, tifPath, domainShp, bandList)
            ## rgb
            # cal.calRGB(tifPath, domainShp)

            ## NDWI
            # cal.calTwoBand(tifPath, domainShp, 'B03', 'B08', 'ndwi.tif', ['calculate', 0])
            # cal.calTwoBand(tifPath, domainShp, 'B03', 'B08', 'ndwiClass.tif', ['class', 0])
            ## HDWI
            # cal.calHDWI(tifPath, tifPath+'hdwi.tif', ['calculate', 0], domainShp)
            # cal.calHDWI(tifPath, tifPath+'hdwiClass.tif', ['class', -0.46], domainShp)
            # cal.calTmpTrueWater()
            # cal.calTmpTrueWater(tifPatth+'hdwi.tif', ['calculate', 0], domainShp, 'tmp\\')
