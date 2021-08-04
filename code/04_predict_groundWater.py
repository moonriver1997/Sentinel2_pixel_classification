import tool.basicTool as bas
# import tool.imageTool as img
# import tool.learningTool as lrn

import tool.groundWater as gdw


domainList = bas.domainList
dataList = bas.dataList

for domain in domainList:
    for data in dataList:
        for times in range(0, 1):
            gdw.predict(domain, '_'.join([domain, data, str(times)]))


