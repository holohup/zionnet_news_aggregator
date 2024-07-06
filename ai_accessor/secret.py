import random
from time import sleep    
import requests
import logging
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem
from dapr.clients.grpc._request import TransactionalStateOperation, TransactionOperationType

#code
logging.basicConfig(level = logging.INFO)
DAPR_STORE_NAME = "localsecretstore"
key = 'secret'

with DaprClient() as client:
    #Using Dapr SDK to get a secret
    secret = client.get_secret(store_name=DAPR_STORE_NAME, key=key)
    logging.info('Result: ')
    logging.info(secret.secret)
    #Using Dapr SDK to get bulk secrets
    secret = client.get_bulk_secret(store_name=DAPR_STORE_NAME)
    logging.info('Result for bulk secret: ')
    logging.info(sorted(secret.secrets.items()))
