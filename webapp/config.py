import cx_Oracle
import yaml
import os

class Config(object):
    pass
class ProdConfig(Config):
    pass
class DevConfig(Config):
    DEBUG = True
    os.environ["NLS_LANG"] = "TRADITIONAL CHINESE_TAIWAN.ZHT16BIG5"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_POOL_SIZE = 20
    #SQLALCHEMY_POOL_TIMEOUT = 5
    #SQLALCHEMY_POOL_RECYCLE = 300
    #SQLALCHEMY_ECHO = False

    # load cfg
    yml_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db.yml')
    with open(yml_path, 'r') as ymlfile:
        _cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    oracle_conn_str = 'oracle+cx_oracle://{username}:{password}@{dsn_str}'
    dsn_str = cx_Oracle.makedsn(_cfg['oracle']['ip'],
                                _cfg['oracle']['port'],
                                _cfg['oracle']['service_name']).replace('SID', 'SERVICE_NAME')
    SQLALCHEMY_DATABASE_URI =   oracle_conn_str.format(
                                    username=_cfg['oracle']['username'],
                                    password=_cfg['oracle']['password'],
                                    dsn_str=dsn_str
                                )
