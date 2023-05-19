from contextlib import contextmanager
from sqlalchemy import DateTime, Integer, String, create_engine,Engine,MetaData, Table, Column, ForeignKey, func,select,join,TableClause,update
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker,relationship
from sqlalchemy import text,TextClause,Table
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
from ._utils import get_plural_name,get_singularize_name

DataMap = None
mapped_base = None
engine:Engine=None 
table_prefix=""
cfg = config.get("database")
if cfg:
    table_prefix = cfg.get("table_prefix","")
class Base(DeclarativeBase):
    __abstract__ = True
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    create_at = Column(DateTime(timezone=True), server_default=func.now())
class Relations():
    @classmethod
    def M2M(self,Tb1:Base,Tb2:Base):
        '''set many to many relationship on :Tb1 and :Tb2'''
        tb2 = get_plural_name(Tb2.__name__.lower())
        tb1 = get_plural_name(Tb1.__name__.lower())
        m2m_table = Table(f"{table_prefix}{tb1}_{tb2}", Base.metadata,
        Column(f'{tb1}_id', Integer, ForeignKey(f'{Tb1.__tablename__}.id'), primary_key=True),
        Column(f'{tb2}_id', Integer, ForeignKey(f'{Tb2.__tablename__}.id'), primary_key=True)
        ) 
        setattr(Tb1,f"{tb2}",relationship(tb2, secondary=m2m_table, back_populates=f"{Tb1.__tablename__}"))
        setattr(Tb2,f"{tb1}",relationship(tb1, secondary=m2m_table, back_populates=f"{Tb2.__tablename__}"))
        #tests
        # if not hasattr(Tb1,'fullname'):
        #     setattr(Tb1,'fullname',Column(String(50) ))
        # if not hasattr(Tb2,'fullname'):
        #     setattr(Tb2,'fullname',Column(String(50) ))
        return m2m_table
    @classmethod
    def M2O(self,Tb1:Base,Tb2:Base):
        '''set 
            :Tb1 belongs to :Tb2
            and :Tb2 hasmany :Tb1
        '''
        _tb1s = Tb1.__tablename__
        _tb2s = Tb2.__tablename__
        tb1 = get_singularize_name(_tb1s)
        tb2 = get_singularize_name(_tb2s)
        
        if not hasattr(Tb1, f"{tb2}_id"):
            setattr(Tb1, f"{tb2}_id",Column(Integer, ForeignKey(f'{tb2}.id'))) 
        if not hasattr(Tb1,f"{tb2}"):
            setattr(Tb1,f"{tb2}",relationship(f'{tb1}',back_populates=f'{tb2}'))
        if not hasattr(Tb2,tb1):
            setattr(Tb2,tb1,relationship(tb1,back_populates=tb2))
        return Tb1,Tb2
    pass
class InitDbError(Exception):
    pass



 
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
 