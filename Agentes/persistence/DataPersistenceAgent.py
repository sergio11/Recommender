import datetime

from BaseAgent import BaseAgent
from pymongo import MongoClient
import pandas as pd
import os.path


class DataPersistenceAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)
        # Service offered by agent

        # Set method for loading routes
        self.bind('REP', alias='getRoutesByUserId', handler=self.get_routes_user_id)


    def setup(self, ns, *args):
        super(DataPersistenceAgent, self).setup(ns, *args)
        self.bss_info = args[0]


    ####################################################################################################################
    ## RAW DATA
    ####################################################################################################################

    def get_routes_user_id(self, arg_dict):
        self.log_info("Getting routes for user {}".format(arg_dict["id"]))

        # TODO this could be loaded in the setup and then served... as you want (or query to de MySQL directly) It's up
        # to you

        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "NY_Restauraunts_checkins.csv")

        df = pd.read_csv(path)


        self.log_info("Total of {} routes obtained from DDBB".format(len(df)))

        return df
