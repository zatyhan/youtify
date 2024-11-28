import os
import redis
from datetime import timedelta

class BaseConfig(object):
    # CACHE_TYPE = os.environ['CACHE_TYPE']
    # CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    # CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    # CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    # CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    # CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']
    SESSION_TYPE = os.environ['SESSION_TYPE']
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ['PERMANENT_SESSION_LIFETIME']))
    SESSION_USE_SIGNER = os.environ['SESSION_USE_SIGNER']
    SESSION_REDIS = redis.from_url(os.environ['SESSION_REDIS'])