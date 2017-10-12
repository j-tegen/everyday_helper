
import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = os.environ['EVERYDAY_DB']
db_uid = os.environ['EVERYDAY_UID']
db_pw = os.environ['EVERYDAY_PW']
server_name = os.environ['EVERYDAY_SERVER']
host_ip = os.environ['EVERYDAY_HOST']
port = os.environ.get('PORT', 5000)
api_version = 'v1'

postgres_local_base = "postgresql://{uid}:{pw}@{server}:5432/".format(server=server_name,
                                                                             uid=db_uid,
                                                                             pw=db_pw)


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATION_ROOT = '/api/{}'.format(api_version)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + db_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + db_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'