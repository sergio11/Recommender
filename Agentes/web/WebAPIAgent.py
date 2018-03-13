import os

from BaseAgent import BaseAgent
import datetime as dt
import pandas as pd

from flask import Flask
from flask import render_template
import json


class WebAPIAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)

    def setup(self, ns, *args):
        BaseAgent.setup(self, ns)

        self.set_attr(bss_info=args[0])
        self.set_attr(predictionAgent=args[1])

        self.create_web_server()
        self.start_web_server()

    def start_web_server(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, use_debugger=False)

    def create_web_server(self):

        cur_path = os.path.dirname(__file__)

        self.app = Flask(__name__)

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

