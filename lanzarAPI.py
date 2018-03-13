# -*- coding: utf-8 -*-
from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import StringIO
import pandas as pd
from sklearn.svm import SVC, LinearSVC, OneClassSVM
from sklearn.externals import joblib
from utiles import make_sure_path_exists, listToCSV
import numpy as np
import csv
from sklearn.model_selection import cross_val_score
from sklearn import preprocessing
import datetime
import geopy.distance

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

rutaModelos = os.path.join(APP_ROOT, "modelos")
defaultPath = "rutas"

make_sure_path_exists(rutaModelos)

n_jobs = -1     # Seleccionando máximo número de cores
verbose = 10    # Seleccionando máximo nivel de mensajes

maxRecomendaciones = 15



def guardarCSV(fichero,nombreDumpModelo):
    # Protegiendo el sistema de posibles nombres de fichero que contengan paths dañinos. http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
    nombreDumpModelo = secure_filename(nombreDumpModelo)

    # generar una carpeta en la que guardar todos los datos basada en la identidad que se le ha dado al modelo de forma que tenga una estructura funcional
    rutaIdModelo = os.path.join(rutaModelos, nombreDumpModelo)
    make_sure_path_exists(rutaIdModelo)

    ###Leer CSV obtenido
    df_leido = pd.read_csv(fichero)
    
    ###PREPROCESAR
    # Rellenando NaN a 0 en variables no categoricas
    categoricals = []
    for col, col_type in df_leido.dtypes.iteritems():
        if col_type == 'O':
            categoricals.append(col)
        else:
            df_leido[col].fillna(0, inplace=True)
        

    # Tranformando variables categoricas a numericas de forma que no haya problemas de ordinalidad
    df_preprocesado = pd.get_dummies(df_leido, dummy_na=True)
    
    # salvando fichero csv de datos de entrenamiento, por si se quieren revisar o reutilizar
    df_leido.to_csv(os.path.join(rutaIdModelo, "data.csv"), index=False)
    
    
    return "Datos cargados"



def recomendar(nombreDumpModelo,id, lat, lon):
    # Protegiendo el sistema de posibles nombres de fichero que contengan paths dañinos. http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
    nombreDumpModelo = secure_filename(nombreDumpModelo)

    # generar una carpeta en la que guardar todos los datos basada en la identidad que se le ha dado al modelo de forma que tenga una estructura funcional
    rutaIdModelo = os.path.join(rutaModelos, nombreDumpModelo)
    make_sure_path_exists(rutaIdModelo)
    rutaFicheroDatos = os.path.join(rutaIdModelo, "data.csv")

    ###Leer CSV de datos completos
    df_leido = pd.read_csv(rutaFicheroDatos)
    df_leido =  df_leido.drop_duplicates()
    
    #coordenadas usuario
    coords_user = (lat, lon)
    
    #calcular distancias de las rutas al usuario
    df_leido['user_distance'] = df_leido.apply( lambda row: geopy.distance.vincenty(coords_user, (row['latitude'],row['longitude'])).km , axis=1 )
    df_leido=df_leido.sort_values(by='user_distance')
    
    
    #filtrado de datos por id_usuario
    filtro=['total_time','distance', 'average_speed','elevation_gain','elevation_loss']
    
    df_train = df_leido.query('id_user_bike_mobile =='+str(id)) #filas
    df_train = df_train.filter(items=filtro)                    #columnas
    
    df_test = df_leido.query('id_user_bike_mobile !='+str(id))  #filas
    df_test = df_test.filter(items=filtro)                      #columnas
    
    n_train=df_train.shape[0]

    if ( n_train > 0 ) :

        #Modelo
        modelo =OneClassSVM(nu=0.9, kernel="linear")
    
        x = df_train
        x = pd.get_dummies(x, dummy_na=True)
    
        x2 = df_test
        x2 = pd.get_dummies(x2, dummy_na=True)

        # Entrenando modelo
        modelo.fit(x)
    
        #Recomendar
        prediccion = modelo.predict(x2)
    
        #Asignar resultado
        df_test['recomendado']=prediccion
    
        #filtrar por los elementos elegidos
        df_prediccion=df_test[ df_test['recomendado'] > 0 ]
        
        #si no hay predicciones, metemos todas las de entrenamiento
        if df_prediccion.shape[0] == 0:
            df_prediccion=df_test
 
    else:
        df_prediccion=df_test
    
    #añadir un columna con los id de ruta
    df_prediccion['id_route']=df_leido['id_route']
    df_prediccion['user_distance']=df_leido['user_distance']
    
    #devolver los maxRecomendaciones primeros
    df_prediccion=df_prediccion[0:maxRecomendaciones]
    n_recomendaciones=df_prediccion.shape[0]
    
    #return df_prediccion['id_route'].to_string()
    return "id:"+str(id)+" lat:"+str(lat)+" lon:"+str(lon)+"\n Numero de rutas del usuario: "+str(n_train)+"\n"+df_train.to_string()+"\n Numero de rutas encontradas: "+str(n_recomendaciones)+"\n"+df_prediccion.to_string()
    
    
    
# Entrada de API REST para recomendar.
""" USO

Tipo de petición: POST

Llamar a: direccion:puerto/recomendar?nombreDumpModelo=nombre&id=id_usuario&lat=latitud&lon=longitud

ENTRADA:
    Parámetros GET:  Enviar por parámetro GET 
                                nombreDumpModelo
                                id
                                lat
                                lon

SALIDA:
    Se almacena en la carpeta modelos, en una carpeta llamada como el nombreDumpModelo aportado, el modelo generado para poder predecir con el así como todos los datos necesarios.

    La petición POST devuelve un mensaje de éxito o de error.

"""
@app.route('/recomendar', methods=['POST', 'PUT'])
def apiRecomendar():
    ### OBTENER PARAMETROS GET
    dataGET = request.args

    
    
    numModelo = None
    if dataGET:
        if "nombreDumpModelo" in dataGET:
            nombreDumpModelo = dataGET["nombreDumpModelo"]
        else:
            nombreDumpModelo = defaultPath
            
        if "id" in dataGET:
            id = dataGET["id"]
        else:
            return "Falta parametro id", 400
            
        if "lat" in dataGET:
            lat = dataGET["lat"]
        else:
            return "Falta parametro lat", 400
            
        if "lon" in dataGET:
            lon = dataGET["lon"]
        else:
            return "Falta parametro lon", 400

    else:
        return "Faltan parametros id,lat,lon", 400
        
    return recomendar(nombreDumpModelo,id,lat,lon)



# Entrada de API REST para recomendar.
""" USO

Tipo de petición: POST

Llamar a: direccion:puerto/recomendar?nombreDumpModelo=nombre&id=id_usuario&lat=latitud&lon=longitud

ENTRADA:
    Parámetros GET:  Enviar por parámetro GET 
                                nombreDumpModelo
                                id
                                lat
                                lon

SALIDA:
    Se almacena en la carpeta modelos, en una carpeta llamada como el nombreDumpModelo aportado, el modelo generado para poder predecir con el así como todos los datos necesarios.

    La petición POST devuelve un mensaje de éxito o de error.

"""
@app.route('/loadCSV', methods=['POST', 'PUT'])
def apiLoad():
    ### OBTENER PARAMETROS GET
    dataGET = request.args

    
    numModelo = None
    if dataGET:
        if "nombreDumpModelo" in dataGET:
            nombreDumpModelo = dataGET["nombreDumpModelo"]
        else:
            nombreDumpModelo = defaultPath
    else:
        nombreDumpModelo = defaultPath


    ###OBTENER FICHERO DE DATOS PARA ENTRENAMIENTO

    # Comprobacion de envio de fichero
    if not 'file' in request.files:
        return "No se ha enviado un archivo como 'file'", 400

    # obtener fichero
    file = request.files['file']

    ###PROCESAR CONTENIDO DEL FICHERO
    # contenido a string
    file_contents_string = file.stream.read().decode("utf-8")

    # string a fichero simulado
    file_string_IO = StringIO.StringIO(file_contents_string)

    ### GUARDAR CSV
    return guardarCSV(file_string_IO,nombreDumpModelo)




    

if __name__ == '__main__':
    app.run(debug=True)


