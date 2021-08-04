import tool.imageTool as img
import tool.basicTool as bas
import tool.waterTool as wat

# dataList = bas.dataList[3:]
# domainList = bas.domainList
# for data in dataList:
#     for domain in domainList:
#         dataFolder = bas.pathWithList(['datasets', domain, data, 'water', 'waterTable'])
#         water = wat.waterVol(dataFolder, domain)
#         print('Domain:', domain, 'Date:', data, 'Water vol:', water, 'm3', water/10000)
#         # water = wat.waterTmp(dataFolder, domain)
#         # print('Domain:', domain, 'Date:', data, 'Water area:', water, 'm2')
        

# domain = '51N_Center'
# for data in dataList:
#     datatFolder = bas.pathWithList(['datasets', domain, data])
#     waterArea =  wat.waterArea(datatFolder, domain+"_01")
#     print('Date:', data, 'Water area:', (waterArea), 'm2')

# for domain in bas.domainList:
#     wat.channel(domain)

domain = '51N_Center'
data = '20180625'
dataFolder = bas.pathWithList(['datasets', domain, data, 'water', 'waterTable'])
water = wat.waterVol(dataFolder, domain)
print('Domain:', domain, 'Date:', data, 'Water vol:', water, 'm3', water/10000)