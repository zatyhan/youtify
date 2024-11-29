import os
import redis
from datetime import timedelta

class BaseConfig(object):
    SESSION_TYPE = os.environ['SESSION_TYPE']
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ['PERMANENT_SESSION_LIFETIME']))
    SESSION_USE_SIGNER = os.environ['SESSION_USE_SIGNER']