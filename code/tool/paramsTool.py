import tool.dbTool as dbs
import tool.basicTool as bas

import time
from selenium import webdriver

def getSunPara (sensingTime, lat, lon):
    excelPath = bas.pathWithList(['lib', 'database']) + 'sunPara.xlsx'
    dataset = dbs.readExcel(excelPath)
    option = 1
    for i in range(0, len(dataset['lon'])):
        if [str(dataset['lat'][i]), str(dataset['lon'][i]), dataset['sensingTime'][i]] == [lat, lon, sensingTime]:
            option = 0
            altitude = dataset['altitude'][i]
            azimuth = dataset['azimuth'][i]
            break
    
    if option == 1:
        chromePath = bas.pathWithList(['lib', 'exe']) + 'chromedriver.exe'
        dataset = dataset.values.tolist()

        urlHead = 'https://www.suncalc.org/#/' + lat + ',' + lon + ',9/' 
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(chromePath, chrome_options=options)
        dateFormat = sensingTime[0:4] + '.' + sensingTime[4:6] + '.' + sensingTime[6:8]
        timeFormat = str(int(sensingTime[9:11]) + 8) + ':' + sensingTime[11:13]
        url = urlHead + dateFormat + '/' + timeFormat + '/1/3'
        driver.get(url)
        time.sleep(5)

        altitude = driver.find_element_by_id("sunhoehe").text
        azimuth = driver.find_element_by_id("azimuth").text

        dataset.append([lat, lon, sensingTime, altitude, azimuth])
        
        time.sleep(5)
        driver.close()
        driver.quit()

        columns = ['lat', 'lon', 'sensingTime', 'altitude', 'azimuth']
        dbs.writeExcel(dataset, columns, excelPath)

    return float(altitude[:-1]), float(azimuth[:-1])

def getSunParaDict (time, location, paraList):
    excelPath = bas.pathWithList(['lib', 'database']) + 'sunPara.xlsx'
    datasets = dbs.readExcel(excelPath)
    dataList = datasets.values.tolist()
    for i in range(0, len(dataList)):
        if datasets['lat'][i] == location[0] or datasets['lon'][i] == location[1] or datasets['sensingTime'][i][0:8] == time:
            returnDic = {}
            for col in datasets.columns[3:]:
                if col in paraList:
                    returnDic[col] = float(datasets[col][i][:-1])
            if returnDic == {}:
                returnDic['none'] = 0
            return returnDic
    return {'none': 0}
