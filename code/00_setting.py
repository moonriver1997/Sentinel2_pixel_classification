import tool.dbTool as dbs
import tool.basicTool as bas

def checkInput (i):
    try:
        val = int(i)
        if len(i) != 8:
            return False
        return True
    except ValueError:
        return False

print('Hello! Welcome to the program setting process.')
mode = input('Please enter the setting mode. (time/domain): ')
while mode != 'time' and mode != 'domain':
    if mode == 'exit':
        break
    print('There is no "'+ mode + '" setting mode.')
    mode = input('Please input again. (time/domain)')

if mode != exit:
    print('Please enter the', mode ,'list of your study, separated by Enter and end with 0 + Enter.')
    print('Enter exit to end the process.')
    if mode == 'time':
        print('time format: yyyymmdd')

    inputList = []
    val = input()
    if mode == 'time':
        while val != '0':
            if checkInput(val):
                inputList.append(val)
            elif val == 'exit':
                break
            else:
                val = print('Format wrong, please input again. (Format: yyyymmdd)')
            val = input()
    else:    
        while val != '0':
            inputList.append(val)
            if val == 'exit':
                break
            val = input()
    print(inputList)
#     if val != 'exit':
#         print(inputList)
#     print(domainList)
#     for domain in domainList:
#         if domain+'.shp' not in bas.getDirList (domainPath):
#             print("Please put", domain+'.shp', "into the domainShp folder, and restart the setting process.")
