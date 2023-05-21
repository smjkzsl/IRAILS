from contextlib import contextmanager
from sqlalchemy import DateTime, Integer, String, create_engine,Engine,MetaData, Table, Column, ForeignKey, func,select,join,TableClause,update
from sqlalchemy.orm import DeclarativeBase,Session,sessionmaker,relationship,Query
from sqlalchemy import text,TextClause,Table
from sqlalchemy.ext.automap import automap_base

from ._utils import camelize_classname,pluralize_collection
 
from alembic import command
from alembic.config import Config
import configparser
import re,os,sys
from typing import Dict, List, Type, Union
from .log import _log
from ._i18n import _,load_app_translations
from .config import config,ROOT_PATH
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
    __all = {}
    @classmethod
    def M2M(self,Tb1:Base,Tb2:Base):
        '''
        set many to many relationship on :Tb1 and :Tb2\n
        :Tb1 will added attribute tb2_tablename(if it's not setted)\n
        :Tb2 will added attribute tb1_tablename(if it's not setted)\n
        will auto created a table named :`Tb1.__tablename__ _ Tb2.__tablename__` and return it\n
        like this:\n
        `Table(f"{database.table_prefix}user_role", database.Base.metadata,\n
        Column('user_id', Integer, ForeignKey(f'{database.table_prefix}users.id'), primary_key=True),\n
            Column('role_id', Integer, ForeignKey(f'{database.table_prefix}roles.id'), primary_key=True)\n
         )`
        '''
        tb2 = get_plural_name(Tb2.__name__.lower())
        tb1 = get_plural_name(Tb1.__name__.lower())
        tb1_naked_name = get_singularize_name(Tb1.__tablename__.replace(table_prefix,""))
        tb2_naked_name = get_singularize_name(Tb2.__tablename__.replace(table_prefix,""))
        m2m_table_name = f"{table_prefix}{tb1_naked_name}_{tb2_naked_name}"
        m2m_table = Table(m2m_table_name, Base.metadata,
        Column(f'{tb1_naked_name}_id', Integer, ForeignKey(f'{Tb1.__tablename__}.id'), primary_key=True),
        Column(f'{tb2_naked_name}_id', Integer, ForeignKey(f'{Tb2.__tablename__}.id'), primary_key=True)
        ) 
        setattr(Tb1,f"{tb2}",relationship(Tb2.__name__, secondary=m2m_table, back_populates=f"{tb1}"))
        setattr(Tb2,f"{tb1}",relationship(Tb1.__name__, secondary=m2m_table, back_populates=f"{tb2}"))
        self.__all[f"M2M{tb1}{tb2}"] = m2m_table
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
                
        # print(f"Creating class {name} in module {module_name}")
        obj = super().__new__(cls, name, bases, attrs)
        if module_package:
            package_module = sys.modules[module_package]
            service_package_path =  package_module.__path__[0]
            app_dirs = service_package_path.split(os.sep)
            if len(app_dirs)>2:
                app_dirs = app_dirs[-2:]
                setattr(obj,"__appdir__",".".join(app_dirs))
                app_dir = os.path.dirname(service_package_path)
                # auto set the i18n locales to the `app_name/locales`
                t = load_app_translations(app_dir)
                setattr(obj,"_",t) #modify object
        return obj

class Service(metaclass=_serviceMeta):
    __all_generated = {}
    engine:Engine = engine
    _ = _ #the i18n traslation object ,it's will auto redirect the `app_name/locales` dir i18n configure
    
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
    def get(self,model:Base,id:int)->Base:
        return self.session().get(model,id)
    @classmethod
    def add(self,model:Union[Type,Base],**kwargs)->Base:
        if isinstance(model,Base):
            m=model
        else:
            if  kwargs  :
                m=model(**kwargs)
        if m:
            session = self.session()
            session.add(m)
            session.commit()
            session.merge(m)
            return m
        return None
    @classmethod
    def list(self,model:Base,**kwargs)->List[Base]:
        session = self.session()  
        query = session.query(model) 
        if kwargs:
            query = query.filter_by(**kwargs) 
        return query.all()
    @classmethod
    def query(self,model:Base)->Query:
        session = self.session()  
        query = session.query(model) 
         
        return query
    
    @classmethod
    def delete(self,model:Base,**kwargs)->int:
        session = self.session()  
        if kwargs:
            cnt = session.query(model).filter_by(**kwargs).delete()
        else:
            cnt = session.query(model).delete()
        session.commit()
        return cnt
    @classmethod
    def update(self,model:Base,filters:Dict=None, values:Dict=None)->Base:
        cnt = 0
        if values:
            session = self.session() 
            cnt = session.query(model).filter_by(**filters).update(values)
            session.commit() 
        return cnt
    @classmethod
    def flush(self,model:Base=None):
        session = self.session()
        if not model:
            return session.commit()
        if not model in session:
            session.merge(model)
        session.commit()
         
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
        """ for `dbfirst` """
        if DataMap:
            return DataMap.tables
        else:
            return {}
    @classmethod
    def mapped(cls,table_name:str): 
        '''
        get the auto mapped table object
        for `dbfirst`
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

def check_migration(engine:Engine,uri,alembic_ini,upgrade=None): 
    alembic_ini = os.path.abspath(os.path.join(ROOT_PATH,alembic_ini))
    def _update_uri_to_ini(): 
        #auto update alembic.ini sqlalchemy.url section 
        
        config = configparser.ConfigParser() 
        # read ini config
        config.read(alembic_ini)
        config.set('alembic','sqlalchemy.url',uri)
        script_location = config.get('alembic','script_location')
        script_location= os.path.abspath(os.path.join(ROOT_PATH,script_location))
        config.set("alembic",'script_location',script_location)
        # save modified ini file
        with open(alembic_ini, 'w') as f:
            config.write(f)
        #makesure the migrations directory exists
        reversions_dir =  os.path.join(script_location,"versions")
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
        msg = msg.replace('_New upgrade operations detected_','').replace("None","").replace(table_prefix,"")
        if 'Target database is not up to date' in msg:
            #check is check,the database version is not matched alembic
            _log.warn(_('Target database is not up to date'))
        else:
            if isinstance(upgrade,bool):
                #call by script ,igonred it
                pass
            else:
                #create revision file
                command.revision(alembic_cfg, autogenerate=True, message=msg) 
        # upgrade the db
    to_revision = 'head'
    if  upgrade is None or upgrade==True: 
        command.upgrade(alembic_cfg, to_revision)    
    else:
        command.downgrade(alembic_cfg,"-1")
def _test_connection():
    #test connect
    try:
        with engine.connect() as conn:
            _log.disabled = False
            _log.debug(_('database connection successed:') + str(conn))

    except Exception as e:
        _log.disabled = False
        _log.error(_("database connection failed!"))  
        raise
        exit(1)  
def init_database(uri: str, debug: bool = False, cfg=None):
    '''
    Initializes the database connection.
    :param uri: SQLAlchemy connection string
    :param debug: Debug mode flag
    :param cfg: The database configuration object
    :return: Returns the engine object if successful, otherwise None
    '''
    if not cfg:
        return None
    if not uri:
        uri = cfg.get("uri", "")
    if not uri:
        return None
    global DataMap, mapped_base, engine, table_prefix
     # Get the database encoding and decoding configurations
    dbencode = cfg.get('dbencode')
    dbdecode = cfg.get('dbdecode')
    
     # Check if the database is sqlite and create the directory
    if uri.startswith('sqlite'):
        
        part = uri.split(':///')
        db_directory  = os.path.dirname(part[1])
        db_directory = os.path.abspath(os.path.join(ROOT_PATH, db_directory))
        db_file = os.path.join(db_directory,os.path.basename(part[1]))
        cfg['uri'] = uri = f"sqlite:///{db_file}"
        os.makedirs(db_directory, exist_ok=True) 
     # Get the maptables and dbfirst configurations
    dbfirst = cfg.get("dbfirst") 
    maptables = cfg.get("maptables") #if configured, only the listed tables will be mapped

     # Create the engine object
    engine = create_engine(uri, echo=False)

    if dbfirst: # Normal database
        def convert_varchar(s):
            # Convert the string encoding to dbencode format
            try:
                return s.encode(dbencode).decode(dbdecode)
            except:
                return s
         # Create a MetaData object and reflect the tables from the database
        DataMap = MetaData() 
        DataMap.reflect(engine, only=maptables)
         # Create the mapped base object
        mapped_base = automap_base(metadata=DataMap)
        mapped_base.prepare(autoload_with=engine,
            classname_for_table=camelize_classname,
            name_for_collection_relationship=pluralize_collection )
        engine.convert_varchar = convert_varchar
     # Test the connection
    _test_connection()
    return engine
