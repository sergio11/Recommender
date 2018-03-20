import datetime

from BaseAgent import BaseAgent
import pandas as pd
import os.path
from werkzeug.utils import secure_filename
from utiles import make_sure_path_exists, listToCSV


class DataPersistenceAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)
        # Service offered by agent

        # Set method for loading routes
        self.bind('REP', alias='getRoutesByUserId', handler=self.get_routes_user_id)
        self.bind('REP', alias='saveCSV', handler=self.saveCSV)


    def setup(self, ns, *args):
        super(DataPersistenceAgent, self).setup(ns, *args)
        self.bss_info = args[0]


    ####################################################################################################################
    ## RAW DATA
    ####################################################################################################################

    def get_routes_user_id(self, arg_dict):
        self.log_info("Getting routes from DDBB")
        
        #Obtener parametros
        nombreDumpModelo=arg_dict["nombreDumpModelo"]
        
        #generar path <
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        rutaModelos = os.path.join(APP_ROOT, "modelos")
        make_sure_path_exists(rutaModelos)
        
        rutaIdModelo = os.path.join(rutaModelos, nombreDumpModelo)
        make_sure_path_exists(rutaIdModelo)
        rutaFicheroDatos = os.path.join(rutaIdModelo, "data.csv")

        ###Leer CSV de datos completos
        df_leido = pd.read_csv(rutaFicheroDatos)
        df_leido = df_leido.drop_duplicates()



        self.log_info("Total of {} routes obtained from DDBB".format(len(df_leido)))

        return df_leido
        
        
        
    def saveCSV(self, arg_dict):
        self.log_info("Saving data in model "+arg_dict["nombreDumpModelo"] )
        
        nombreDumpModelo=arg_dict["nombreDumpModelo"]
        file_string_IO=arg_dict["file_string_IO"]

        # TODO this could be loaded in the setup and then served... as you want (or query to de MySQL directly) It's up
        # to you
        return self.guardarCSV(file_string_IO,nombreDumpModelo)
        

        return 'ok'
        
        
    def guardarCSV(self, fichero,nombreDumpModelo):
        # Protegiendo el sistema de posibles nombres de fichero que contengan paths dañinos. http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
        nombreDumpModelo = secure_filename(nombreDumpModelo)
        
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))

        rutaModelos = os.path.join(APP_ROOT, "modelos")
        make_sure_path_exists(rutaModelos)

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
    
    
        return "ok"
