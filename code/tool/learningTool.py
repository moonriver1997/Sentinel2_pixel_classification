import tool.basicTool as bas
import tool.imageTool as img
import tool.paramsTool as par

import numpy as np
import keras
from keras import regularizers
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

sentinelBand = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B11', 'B12', 'B8A']


# ===
def predict_GroundWater (modelName, X):
    print('Predict')
    model = load_model(modelName)
    y_predict = model.predict(X)
    print(np.max(y_predict))
    print(np.min(y_predict))
    return y_predict

def training_GroundWater (X, y, X_test, y_test, modelName):
    epochs = 500
    batchSize = 128
    inputSize = len(X[0])
    loss='mean_absolute_error'
    optimizer = 'adam'
    model = Sequential()
    model.add(Dense(4, activation='relu', input_dim=inputSize))
    model.add(Dense(1,activation='linear'))
    model.compile(loss=loss, optimizer=optimizer)
    model.summary()

    X_train, y_train, X_val, y_val = splitData(X, y , 0.1)
    callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batchSize, validation_data=(X_val, y_val), callbacks=[callback])

    score = model.evaluate(X_test, y_test, batch_size=batchSize)
    model.save(modelName)
    y_predict = model.predict(X_test)
    print(y_predict)
    print(np.max(y_predict))
    print(np.min(y_predict))
    print(score)
    return [score, history.history]

def normalize_GroundWater (X):
    scaler = MinMaxScaler()
    scaler.fit(X)
    return scaler.transform(X), list(scaler.data_max_), list(scaler.data_min_)

# ===
def training_PixelClassification_para (X, y, X_test, y_test, modelName, optimizer, neuron):
    epochs = 500
    batchSize = 128
    inputSize = len(X[0])

    metrics = ['accuracy']
    loss = 'sparse_categorical_crossentropy'
    # optimizer = 'sgd'

    model = Sequential()
    model.add(Dense(neuron, activation='relu', input_dim=inputSize, kernel_regularizer= regularizers.l2(0.001)))
    # output layer
    model.add(Dense(2, activation='softmax'))

    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
    model.summary()
    X_train, y_train, X_val, y_val = splitData(X, y , 0.1)
    callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batchSize, validation_data=(X_val, y_val), callbacks=[callback])

    score = model.evaluate(X_test, y_test, batch_size=batchSize)
    model.save(modelName)

    y_predict = model.predict_classes(X_test)

    print('water pixel ---')
    print('Predict:', np.sum(y_predict))
    print('True:', np.sum(y_test))

    print('Score: ', score)
    return [score, history.history]

def training_PixelClassification_2 (X, y, X_test, y_test, modelName):
    epochs = 500
    batchSize = 128
    inputSize = len(X[0])

    metrics = ['accuracy']
    loss = 'sparse_categorical_crossentropy'
    optimizer = 'sgd'

    model = Sequential()
    model.add(Dense(256, activation='relu', input_dim=inputSize, kernel_regularizer= regularizers.l2(0.001)))
    
    model.add(Dropout(0.5))
    model.add(Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001)))
    
    # output layer
    model.add(Dense(2, activation='softmax'))
    # model.add(Dense(2, activation='sigmoid'))

    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
    model.summary()
    X_train, y_train, X_val, y_val = splitData(X, y , 0.1)
    callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batchSize, validation_data=(X_val, y_val), callbacks=[callback])

    score = model.evaluate(X_test, y_test, batch_size=batchSize)
    model.save(modelName)

    y_predict = model.predict_classes(X_test)

    print('water pixel ---')
    print('Predict:', np.sum(y_predict))
    print('True:', np.sum(y_test))

    print('Score: ', score)
    return [score, history.history]

# ===
def predict_PixelClassification (modelName, X):
    print('Predict')
    model = load_model(modelName)
    return model.predict_classes(X)

def training_PixelClassification (X, y, X_test, y_test, modelName):
    epochs = 500
    batchSize = 128
    inputSize = len(X[0])

    metrics = ['accuracy']
    loss = 'sparse_categorical_crossentropy'
    # optimizer = 'sgd'
    # loss = 'categorical_crossentropy'
    optimizer = 'nadam'

    model = Sequential()
    model.add(Dense(14, activation='relu', input_dim=inputSize))
    # model.add(Dense(4, activation='relu', input_dim=inputSize))
    # model.add(Dense(256, activation='relu', input_dim=inputSize, kernel_regularizer= regularizers.l2(0.001)))
    # model.add(Dropout(0.5))
    # model.add(Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001)))
    # output layer
    model.add(Dense(2, activation='softmax'))
    # model.add(Dense(2, activation='sigmoid'))

    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
    model.summary()
    X_train, y_train, X_val, y_val = splitData(X, y , 0.1)
    callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batchSize, validation_data=(X_val, y_val), callbacks=[callback])

    score = model.evaluate(X_test, y_test, batch_size=batchSize)
    model.save(modelName)

    y_predict = model.predict_classes(X_test)

    print('water pixel ---')
    print('Predict:', np.sum(y_predict))
    print('True:', np.sum(y_test))

    print('Score: ', score)
    return [score, history.history]

# ===
def splitData(X, y, rate):
    X_train = X[int(X.shape[0]*rate):]
    y_train = y[int(y.shape[0]*rate):]
    X_val = X[:int(X.shape[0]*rate)]
    y_val = y[:int(y.shape[0]*rate)]
    return X_train, y_train, X_val, y_val

def normalize_y (y):
    # norm = np.linalg.norm(y)
    # normal_array = y/norm
    normal_array = (y - np.min(y)) / (np.max(y) - np.min(y))
    # print(np.max(normal_array))
    # print(np.min(normal_array))
    return normal_array

def normalize_X (X):
    scaler = MinMaxScaler()
    scaler.fit(X)
    return scaler.transform(X)
# ===
def build_X(rangeArr, domain, dataList, bandList, paraList):
    print('Build: Feature')
    X = []
    for data in dataList:
        file = bas.pathWithList(['datasets', domain, data])
        print('Read file: ', file)
        paramsDict = par.getSunParaDict(data, [bas.lat, bas.lon], paraList)
        X = dataConcatenate(X, getFeature(bandList, rangeArr, file, paramsDict))
    return np.array(X)

def build_y(rangeArr, domain, dataList, targetFile):
    print('Build: Target')
    y = []
    for data in dataList:
        file = bas.pathWithList(['datasets', domain, data]) + targetFile + '.tif'
        if targetFile == 'dem':
            file = bas.getDomainFile(domain, 'dem')
        print('Read file: ', file)
        y = dataConcatenate(y, getTarget(rangeArr, file))
    return y

def getFeature (featureList, rangeArr, dataFolder, paramsDict):
    print("Get feature...")
    for feature in featureList:
        if feature in sentinelBand or feature in ['hillshade']:
            print('Read band: ', feature)
            filePath = dataFolder + feature + '.tif'
        else:
            print('Read: ', feature)
            domain = dataFolder.split(bas.fileSep)[4]
            if feature == 'dem':
                filePath = bas.getDomainFile(domain, 'dem')
            else:
                filePath = bas.pathWithList(['datasets', domain, 'topographic']) + feature + '.tif'
        data = img.setData(rangeArr, img.getImgArr(filePath))

        if feature == featureList[0]:
            featureData = data
        else:
            featureData = np.vstack((featureData, data))

    for j in paramsDict:
        if j != 'none':
            featureData = np.vstack((featureData, np.full(len(data), paramsDict[j])))
    return np.array(featureData.T) 

def getTarget (rangeArr, file):
    return img.setData(rangeArr, img.getImgArr(file))

# ===
def dataConcatenate (dataList, data):
    if dataList == []:
        dataOut = data
    else:
        dataOut = np.concatenate((dataList, data))
    return dataOut
