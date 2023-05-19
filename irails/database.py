from contextlib import contextmanager
from sqlalchemy import DateTime, create_engine,Engine,MetaData, Table, Column, ForeignKey, func,select,join,TableClause,update
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker
from sqlalchemy import text,TextClause
from sqlalchemy.ext.automap import automap_base

from ._utils import camelize_classname,pluralize_collection
 
from alembic import command
from alembic.config import Config
import configparser
import re,os,sys
from typing import Union
from .log import _log
from ._i18n import _,load_app_translations
from .config import config
DataMap = None
mapped_base = None
engine:Engine=None 
table_prefix=""
cfg = config.get("database")
if cfg:
    table_prefix = cfg.get("table_prefix","")

class InitDbError(Exception):
    pass
class Base(DeclarativeBase):
    __abstract__ = True
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    create_at = Column(DateTime(timezone=True), server_default=func.now())


 
class _serviceMeta(type):
    def __new__(cls, name, bases, attrs):
        module_name = attrs['__module__']
        module = sys.modules[module_name]
        module_package = module.__package__
        
                
        print(f"Creating class {name} in module {module_name}")
        obj = super().__new__(cls, name, bases, attrs)
        if module_package:
            package_module = sys.modules[module_package]
            service_package_path =  package_module.__path__[0]
            app_dirs = service_package_path.split(os.sep)
            if len(app_dirs)>2:
                app_dirs = app_dirs[-2:]
                setattr(obj,"__appdir__",".".join(app_dirs))
                app_dir = os.path.dirname(service_package_path)
                t = load_app_translations(app_dir)
                setattr(obj,"_",t)
        return obj

class Service(metaclass=_serviceMeta):
    __all_generated = {}
    engine:Engine = engine
    _ = _
    
    @classmethod
    def session(self)->Session:
        if hasattr(self,"_session"):
            return self._session
        if hasattr(self,'_session_local'):
            session_local = getattr(self,'_session_local')
        else:
            session_local =  sessionmaker(bind=engine)
            setattr(self,"_session_local", session_local) #cache sessionmaker object
        session = session_local()
        setattr(self,"_session",session)
        return session
    
    @classmethod
    @contextmanager 
    def get_session(cls):
        """Provide a transactional scope around a series of operations."""
        if not cls.engine:
            yield None
            return
        if hasattr(cls,'_session_local'):
            session_local = getattr(cls,'_session_local')
        else:
            session_local =  sessionmaker(bind=engine)
            setattr(cls,"_session_local", session_local) #cache sessionmaker object
        session = session_local()
         
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    @classmethod
    def execute(cls,cmd:Union[str,TextClause],**kwargs):
        if not isinstance(cmd,TextClause):
            cmd = text(str)
        with engine.begin() as conn:
            ret = conn.execute(cmd,**kwargs)
        return ret
    @classmethod
    def get_all_mapped_tables(cls):
        if DataMap:
            return DataMap.tables
        else:
            return {}
    @classmethod
    def mapped(cls,table_name:str): 
        '''
        get the auto mapped table object
        '''
        assert table_name
        if not DataMap :
            return None
        if hasattr(mapped_base.classes,table_name):
            return getattr(mapped_base.classes,table_name)
        
        class tblClass(object):
            _tableItem:Table=None 
            def __getattr__(self, __name: str) : 
                return self._tableItem.columns[__name]
            def __getitem__(self,__name:str):
                return self._tableItem.columns[__name]
            pass

        if table_name in cls.__all_generated:return cls.__all_generated[table_name]
        if table_name in DataMap.tables: 
            tbl = DataMap.tables[table_name]
            tbItem = tblClass()
            setattr(tbItem,"_tableItem",tbl) 
            cls.__all_generated[table_name] = tbItem
            return tbItem
        else:
            raise NameError()


            
# def ismongo_cloud(uri):
#     import re 
#     # uri = 'mongodb+srv://dbbruce:smjk123@atlascluster.siz4vrp.mongodb.net/?retryWrites=true&w=majority' 
#     # 匹配 MongoDB Cloud 连接字符串的正则表达式
#     regex = re.compile("mongodb\+srv:\/\/.*@.*\.mongodb\.net\/.*\?.*") 
#     return regex.match(uri)
      

def sanitize_path(path):
    # 匹配非法字符
    illegal_chars = r'[\\/:\*\?"<>\|]'
    # 将非法字符替换为下划线
    sanitized_path = re.sub(illegal_chars, '_', path)
    return sanitized_path

def check_migration(engine:Engine,uri,alembic_ini): 
    def _update_uri_to_ini(): 
        #auto update alembic.ini sqlalchemy.url section 
        config = configparser.ConfigParser() 
        # read ini config
        config.read(alembic_ini)
        config.set('alembic','sqlalchemy.url',uri)
        # save modified ini file
        with open(alembic_ini, 'w') as f:
            config.write(f)
        #makesure the migrations directory exists
        reversions_dir = config.get("alembic",'script_location')
        reversions_dir = os.path.join(reversions_dir,"versions")
        if not os.path.exists(reversions_dir):
            os.makedirs(reversions_dir,exist_ok=True)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise InitDbError(e.args)
    _update_uri_to_ini()
    #  
    alembic_cfg = Config(alembic_ini)    
    try:
        command.check(config=alembic_cfg)
    except Exception as e: 
        msg = sanitize_path(str(e.args)) 
        command.revision(alembic_cfg, autogenerate=True, message=msg) 
        # upgrade the db
        command.upgrade(alembic_cfg, "head") 
def get_engine():
    global engine
    return engine
def init_database( uri:str,debug:bool=False,cfg=None):
    '''
    :uri sqlalchemy connection string
    :params debug mode of debug 
    :cfg the database configure object
    '''
    if not cfg:
        return None
    if not uri:
        uri = cfg.get("uri","")
    if not uri:
        return None
    global DataMap,mapped_base ,engine,table_prefix
    
    
    dbencode = cfg.get('dbencode')
    dbdecode = cfg.get('dbdecode')
    if uri.startswith('sqlite'):
        from .config import ROOT_PATH
        db_directory = os.path.dirname(uri.split(':///')[1])
        os.makedirs(os.path.join(ROOT_PATH, db_directory), exist_ok=True) 

    engine = create_engine(uri,  echo=False)
    dbfirst = cfg.get("dbfirst")
    maptables = cfg.get("maptables")
    
    if not dbfirst :
        pass
    elif dbfirst: 
        def convert_varchar(s): 
            try:
                return s.encode(dbencode).decode(dbdecode)
            except:
                return s
            
        # produce our own MetaData object
        DataMap = MetaData() 
        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        DataMap.reflect(engine, only=maptables)
        # we can then produce a set of mappings from this MetaData.
        mapped_base = automap_base(metadata=DataMap)
        mapped_base.prepare(autoload_with=engine,
            classname_for_table=camelize_classname,
            name_for_collection_relationship=pluralize_collection )
         
        engine.convert_varchar = convert_varchar
 
        pass
    #test connect
    try:
        with engine.connect() as conn:
            _log.disabled = False
            _log.debug('database connection successed:' + str(conn))

    except Exception as e:
        _log.disabled = False
        _log.error("database connection failed!")  
         
        exit(1)  

    return engine
 