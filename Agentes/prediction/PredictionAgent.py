import json

from BaseAgent import BaseAgent


class PredictionAgent(BaseAgent):
    def on_init(self):
        # Define own connection
        BaseAgent.on_init(self)

    def setup(self, ns, *args):
        # Set persistence agent
        self.set_attr(bss_info=args[0])
        self.set_attr(persistenceDataAgent=args[1])

        # Set method for loading routes
        self.bind('REP', alias='getPredictionForUser', handler=self.get_prediction_for_user)



    def get_prediction_for_user(self, args):
        # Load model (models)
        self.log_info("Loading model ..")

        # Request user routes
        self.log_info("Connecting to Persistence agent...")

        # Example synchronous request with args
        df = super(PredictionAgent, self).send_message_to_agent_synchronous(self.persistenceDataAgent,
                                                                                         'getRoutesByUserId', args)

        self.log_info("Loaded routes... Generating predictions")

        # TODO GENERATE PREDICTIONS WITH SOME FANCY ALGORITHM


        self.log_info("Returning predictions")

        # Return predictions
        return df