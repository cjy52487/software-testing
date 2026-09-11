import urllib.parse

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'your-secret-key-here'

    DIALCT = "mysql"
    DRITVER = "pymysql"
    HOST = 'localhost'
    PORT = "3306"
    USERNAME = "root"
    PASSWORD = "MYSQL14yhl9t."
    DBNAME = 'dba'

    SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None

    SESSION_TYPE = 'redis'
    SESSION_REDIS = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    CORS_ORIGINS = "*"
    CORS_SUPPORTS_CREDENTIALS = True