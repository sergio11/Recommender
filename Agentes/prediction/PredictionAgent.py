import json

from BaseAgent import BaseAgent
import os
import geopy.distance
import pandas as pd
from sklearn.svm import SVC, LinearSVC, OneClassSVM
from sklearn.externals import joblib


class PredictionAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)
        self.maxRecomendaciones = 15

    def setup(self, ns, *args):
        # Set persistence agent
        self.set_attr(bss_info=args[0])
        self.set_attr(persistenceDataAgent=args[1])

        # Set method for loading routes
        self.bind('REP', alias='getRecommendations', handler=self.get_recommendations)



    def get_recommendations(self, args):
        # Load model (models)
        self.log_info("Loading data")

        # Request user routes
        self.log_info("Connecting to Persistence agent...")

        # Example synchronous request with args
        df_leido = super(PredictionAgent, self).send_message_to_agent_synchronous(self.persistenceDataAgent,
                                                                                         'getRoutesByUserId', args)

        self.log_info("Data received")
        

        #Obtener parametros
        id=args["id"]
        lat=args["latitude"]
        lon=args["longitude"]
        
        self.log_info("Generating recommendations for user {}".format(id))
       
        #coordenadas usuario
        coords_user = (lat, lon)
    
        #calcular distancias de las rutas al usuario
        df_leido.loc[:,'user_distance'] = df_leido.apply( lambda row: geopy.distance.vincenty(coords_user, (row['latitude'],row['longitude'])).km , axis=1 )
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
            df_test.loc[:,'recomendado']=prediccion
    
            #filtrar por los elementos elegidos
            df_prediccion=df_test[ df_test['recomendado'] > 0 ]
        
            #si no hay predicciones, metemos todas las de entrenamiento
            if df_prediccion.shape[0] == 0:
                df_prediccion=df_test
 
        else:
            df_prediccion=df_test
    
        #añadir columnas con los id de ruta y distancia al usuario
        df_prediccion=df_prediccion.join(df_leido[['id_hash','id_route','user_distance']])
        
        self.log_info("{} routes found".format(len(df_prediccion)))
    
        #devolver los maxRecomendaciones primeros
        df_prediccion=df_prediccion[0:self.maxRecomendaciones]
        n_recomendaciones=df_prediccion.shape[0]
        
        
        self.log_info("{} routes selected".format(len(df_prediccion)))

        self.log_info("Returning recommendations")

        # Return predictions
        return df_prediccion