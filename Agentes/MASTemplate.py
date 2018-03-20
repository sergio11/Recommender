import time

from osbrain import run_agent
from osbrain import run_nameserver

from persistence.DataPersistenceAgent import DataPersistenceAgent
from prediction.PredictionAgent import PredictionAgent
from web.WebAPIAgent import WebAPIAgent
import json

if __name__ == '__main__':

    """
    MULTI AGENT SYSTEM TEMPLATE
    Initially, this MAS will be deployed locally, each agent could be deployed in an indenpent machine.
    """

    # This is employed as dictionary for a global configuration provided to the agents in their init
    bss_info = {
    }

    # System deployment
    ns = run_nameserver()

    # Agent spawn
    dataPersistenceAgent = run_agent('dataPersistenceAgent', base=DataPersistenceAgent)
    predictionAgent = run_agent('predictionAgent', base=PredictionAgent)
    webAgent = run_agent('webAgent', base=WebAPIAgent)

    # Initialize agents with their agent dependencies
    dataPersistenceAgent.setup(ns,bss_info)
    predictionAgent.setup(ns, bss_info, dataPersistenceAgent)
    webAgent.setup(ns, bss_info, predictionAgent,dataPersistenceAgent)


    while True:
        time.sleep(1000000)
