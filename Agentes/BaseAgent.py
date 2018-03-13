from osbrain import Agent
import datetime as dt
import pandas as pd

from flask import Flask
from flask import render_template
import json

class BaseAgent(Agent):
    def on_init(self):
        # Define own connection
        self.bind('PUB', alias='base')
        self.connect(self.addr('base'), alias='base', handler=self.base_message_handler)

    def setup(self, ns, *args):
        pass

    def base_message_handler(self, message):
        self.log_info(message)

    def send_message_to_agent_synchronous(self, agent, method_alias, dict_arg):
        self.connect(agent.addr(method_alias), alias=method_alias)
        self.send(method_alias, message=dict_arg)
        return self.recv(method_alias)
