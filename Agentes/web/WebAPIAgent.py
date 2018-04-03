import os

from BaseAgent import BaseAgent
import datetime as dt
import pandas as pd

from flask import Flask, request
from flask import render_template
import json

from utiles import make_sure_path_exists, listToCSV
from io import StringIO
import io





class WebAPIAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)

    def setup(self, ns, *args):
        BaseAgent.setup(self, ns)

        self.set_attr(bss_info=args[0])
        self.set_attr(predictionAgent=args[1])
        self.set_attr(persistenceAgent=args[2])

        self.create_web_server()
        self.start_web_server()

    def start_web_server(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, use_debugger=False)

    def create_web_server(self):

        #cur_path = os.path.dirname(__file__)

        self.app = Flask(__name__)
        
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))

        rutaModelos = os.path.join(APP_ROOT, "modelos")
        defaultPath = "rutas"

        make_sure_path_exists(rutaModelos)

        # WEB PAGES
        @self.app.route("/")
        def index():
            return render_template("index.html")

        # API
        @self.app.route('/getPrediction/<int:user_id>/<float:latitude>/<float:longitude>')
        def getPrediction(user_id, latitude, longitude):

            result = pd.DataFrame()

            # Request user routes
            args = {"id": user_id, "latitude":latitude, "longitude":longitude}

            self.log_info("Connecting to prediction agent...")

            # Example synchronous request with args
            df = super(WebAPIAgent, self).send_message_to_agent_synchronous(self.predictionAgent,
                                                                                'getPredictionForUser', args)

            self.log_info("Predictions obtained...")


            return df.to_json(orient='records')
            
            
        # Entrada de API REST para recomendar.
        """ USO
        Tipo de petición: POST
        Llamar a: direccion:puerto/recomendar?nombreDumpModelo=nombre&id=id_usuario&lat=latitud&lon=longitud
        """
        @self.app.route('/recomendar', methods=['POST', 'PUT'])
        def apiRecomendar():
            self.log_info("I received a recommendation request")
            
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
                
            # Request user routes
            args = {"nombreDumpModelo": nombreDumpModelo, "id": id, "latitude":lat, "longitude":lon}

            self.log_info("Connecting to prediction agent...")

            # Example synchronous request with args
            df = super(WebAPIAgent, self).send_message_to_agent_synchronous(self.predictionAgent,'getRecommendations', args)   
            
            self.log_info("I received {} routes".format(len(df))  )       
            self.log_info("Sending recommendations to user")                                                        
        
            #return recomendar(nombreDumpModelo,id,lat,lon)
            #return str(df['id_route'].values) 
            return str(df['id_route'].values.tolist())



        # Entrada de API REST para recomendar.
        """ 
        Tipo de petición: POST
        Llamar a: direccion:puerto/recomendar?nombreDumpModelo=nombre&id=id_usuario&lat=latitud&lon=longitud
        """
        @self.app.route('/loadCSV', methods=['POST', 'PUT'])
        def apiLoad():
            self.log_info("I received a loadCSV request")
            
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
            file_string_IO = io.StringIO(file_contents_string)
            
             # Request user routes
            args = {"nombreDumpModelo": nombreDumpModelo,"file_string_IO": file_string_IO}

            self.log_info("Connecting to Persistence agent to store data...")

            # Example synchronous request with args
            df = super(WebAPIAgent, self).send_message_to_agent_synchronous(self.persistenceAgent,
                                                                                'saveCSV', args)

            self.log_info("Response of Persistence agent: "+df)
            
            return df



