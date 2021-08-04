import tool.basicTool as bas
import tool.sentinelTool as sen
tileList = bas.tileList
dateFrom = '2021-02-02'
dateTo = '2021-02-18'
location = [[120.18103132161963, 24.45223275159691], 
            [120.17508202583593, 23.849685120630014],
            [121.24592258743841, 23.838802598496187],
            [121.24592258743841, 24.43598514904619],
            [120.18103132161963, 24.45223275159691],
            [120.18103132161963, 24.45223275159691]]

sen.downloadFile(location, dateFrom, dateTo, tileList)
# # timeList = sen.upgradeSentinel()
# timeList = ['20200215T022759']
# for time in timeList:
#     sen.getL1AJP2(time)