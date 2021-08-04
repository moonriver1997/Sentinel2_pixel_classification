import pandas as pd

def writeExcel (dataset, col, excelPath):
    toExcel(formatData(dataset, col), excelPath)

def toExcel (df, excelPath):
    try:
        df.to_excel(excelPath, index=None)
        print('Excel out, path:', excelPath)
        return 0
    except Exception:
        return -1

def readExcel (excelPath):
    return pd.read_excel(excelPath)

def formatData (dataset, col):
    return pd.DataFrame(dataset, columns=col)