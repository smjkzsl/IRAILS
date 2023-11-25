import configparser
from datetime import datetime, date
import re,os,sys,json
from typing import Any, Dict, List, Optional, Tuple, Type, Union, overload
from contextlib import contextmanager
from sqlalchemy.util._collections import OrderedDict
from sqlalchemy import (Boolean, DateTime, Integer, 
                        String, Text, 
                        create_engine,
                        Engine,
                        MetaData, 
                        Table, 
                        Column, 
                        ForeignKey, 
                        func,
                        select,join,
                        TableClause,
                        update,insert,delete,
                        event,text,TextClause,Table,
                        inspect)
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase,Session,relationship,Query ,attributes
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.sql._typing import _ColumnsClauseArgument
from alembic import command
from alembic.config import Config 
from ._utils import camelize_classname,pluralize_collection ,iJSONEncoder
from .log import _log
from ._i18n import _ #,set_module_i18n
from .config import config,ROOT_PATH
from ._utils import get_plural_name,get_singularize_name
 
EVENTS={
'before_insert', 
'after_insert', 
'before_update', 
'after_update',
'before_delete',
'after_delete', 
'before_attach',
'after_attach', 
'before_commit',
'after_commit',
'before_rollback',
'after_rollback',
'after_soft_delete',
'after_bulk_update', 
'after_bulk_delete',
'before_flush', 
'after_flush',
}

 
DataMap = None
mapped_base = None
engine:Engine=None 
table_prefix=""
cfg = config.get("database")
is_deleted_field = 'is_deleted'
i18n_json_data_field = 'i18n_json_data'
page_size = 20
if cfg:
    table_prefix = cfg.get("table_prefix","")
    page_size = int(cfg.get("page_size",20))
    if page_size<0 :
        page_size=20
    is_deleted_field = cfg.get("is_deleted_field",'is_deleted')
    i18n_json_data_field = cfg.get("i18n_json_data_field",'i18n_json_data')



            
class Base(DeclarativeBase):
    __abstract__ = True 
    __allow_unmapped__ = True
    __table_args__ = {'extend_existing': True}

     
    '''not show in model manager columns names'''
    filter_columns_in_manager = []
    def __init_subclass__(cls,*args,**kwargs) -> None: 

        #auto set table_prefix
        if hasattr(cls,'__tablename__'):
            _tbname:str = getattr(cls,"__tablename__")
            if _tbname and table_prefix and not _tbname.startswith(table_prefix):
                setattr(cls,'__tablename__',f'{table_prefix}{_tbname}')
        else:
            _tbname = table_prefix + get_plural_name(cls.__name__)        
            setattr(cls,'__tablename__',_tbname)
        
        super().__init_subclass__(*args,**kwargs)
        for e in EVENTS:
            if hasattr(cls,e) and callable(getattr(cls,e)):
                    event.listen(cls, e, getattr(cls,e)) 
        
        metas = inspect(cls)
        for col in metas.columns:
            func_name = f"on_change_{col.name}"
            if hasattr(cls,func_name):
                func = getattr(cls,func_name)
                if callable(func) and not hasattr(func,'attched_event'):
                    event.listen(getattr(cls,col.name),'set',func,retval=True)
                    setattr(func,"attched_event",True)
        # if not hasattr(cls,'__system__') or not getattr(cls,"__system__") is True:
        #     set_module_i18n(cls,cls.__module__)
    
    @classmethod
    def _general_columns(self)->Tuple[Column]:
        """return general columns """
        if hasattr(self,'__general_columns__'):
            return self.__general_columns__
        metas = inspect(self)
        ret = tuple(col for colname,col in metas.columns.items() if col.key not in self.filter_columns_in_manager)
        setattr(self,'__general_columns__',ret)
        return ret
    
        
class Schemes():
    _all_m2m_tables_ = {}
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
        if not f"M2M{tb1}{tb2}" in self._all_m2m_tables_:
            m2m_table = Table(m2m_table_name, Base.metadata,
                Column(f'{tb1_naked_name}_id', Integer, ForeignKey(f'{Tb1.__tablename__}.id'), primary_key=True  ),
                Column(f'{tb2_naked_name}_id', Integer, ForeignKey(f'{Tb2.__tablename__}.id'), primary_key=True) 
            , keep_existing=True 
            ) 
            setattr(Tb1,f"{tb2}",relationship(Tb2.__name__, secondary=m2m_table, back_populates=f"{tb1}",passive_deletes=False  ))
            setattr(Tb2,f"{tb1}",relationship(Tb1.__name__, secondary=m2m_table, back_populates=f"{tb2}",passive_deletes=False ))
            self._all_m2m_tables_[f"M2M{tb1}{tb2}"] = m2m_table
        return self._all_m2m_tables_[f"M2M{tb1}{tb2}"]
    @classmethod
    def M2O(self, ChildTable: Base, ParentTable: Base,cascade='delete,all'):
        '''set 
        :ChildTable belongs to :ParentTable
        and :ParentTable hasmany :ChildTable
        '''
        child_tablename = ChildTable.__tablename__
        parent_tablename = ParentTable.__tablename__ 
        child_tbname = get_singularize_name(child_tablename.replace(table_prefix,""))
        parent_tbname = get_singularize_name(parent_tablename.replace(table_prefix,""))
        field_name_of_children = get_plural_name(child_tbname)
        if not hasattr(ChildTable,f"{parent_tbname}_id"):
            setattr(ChildTable, f"{parent_tbname}_id", Column(Integer, ForeignKey(f'{parent_tablename}.id')))
            setattr(ChildTable, f"{parent_tbname}", relationship(ParentTable.__name__, back_populates=f'{field_name_of_children}'))
            setattr(ParentTable, field_name_of_children, relationship(ChildTable.__name__, back_populates=f'{parent_tbname}', cascade=cascade))
        return ChildTable, ParentTable

    @classmethod
    def SOFT_DELETE(self,*tables):
        """
        set a `is_deleted` field on :tables
        please use irails.service to query ,it will auto add the 'is_deleted' flag
        """
        for Tb in tables:
            if not hasattr(Tb,is_deleted_field):
                setattr(Tb,is_deleted_field,Column(Boolean, default=False))
    @classmethod
    def I18NABLE(self,*tables):
        #i18n_json_data={
        #       'col1':{
        #           'en':'bruce',
        #           'zh':'布鲁斯'
        #       },
        #       'col2':{
        #           'en':'hellow',
        #           'zh':'你好'
        #       },
        #       ....
        # 
        # }
        for tb in tables:
            if not hasattr(tb,i18n_json_data_field):
                setattr(tb,i18n_json_data_field,Column(Text,server_default='{}',info={'json':True}))

    @classmethod
    def TIMESTAMPS(self,*tables):
        '''add timestamp(update_at,create_at) field on :tables'''
        for tb in tables:
            if not hasattr(tb,'update_at'):
                tb.update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
            if not hasattr(tb,'create_at'):
                tb.create_at = Column(DateTime(timezone=True), server_default=func.now())        
class InitDbError(Exception):
    pass

def get_model(model_name:str,module_name:str="")->Base:
    module = None
    model:Base = None
    if module_name:
        module =  sys.modules[module_name] if module_name in sys.modules else None
        model = getattr(module,model_name)
    else:
        if module_name in globals():
            module = globals()[module_name]
            model = getattr(module,model_name)
    if model  :
        return model
    else:
        return None
    
    
def get_meta(model_name: str = "") -> Dict[str, List]:
    from sqlalchemy.orm import RelationshipProperty
    def get_subclasses_meta(_cls: Type['Base']) -> Dict[str, List]:
        ret = {}
        for subclass in _cls.__subclasses__():
            metas = inspect(subclass)
            # _general_columns = subclass._general_columns()
            _real_columns = [attr for attr in metas.attrs if not isinstance(attr, RelationshipProperty)]
             
            if subclass.filter_columns_in_manager:
                _real_columns = [col for col in _real_columns if col.key not in subclass.filter_columns_in_manager]   
            
            _relationships = {}
            for attr in metas.attrs:
                if isinstance(attr, RelationshipProperty):
                    relationship = {
                        'type': attr.mapper.class_.__module__ + '.' + attr.mapper.class_.__name__,
                        'uselist': attr.uselist,
                        'backref': attr.backref
                    }
                    _relationships[attr.key] = relationship
            ret[subclass.__module__ + "." + subclass.__name__] = {
                'module': subclass.__module__,
                'columns': _real_columns,
                # '_general_columns':_general_columns,
                'relationships': _relationships
            }
        return ret
    
    ret = get_subclasses_meta(Base)
    _maped = {}
    for item, infos in ret.items(): 
        columns = infos['columns']
        relationships = infos['relationships']
        cols = []
        for _col in columns:
            col = _col.columns[0] if _col.columns else None
            if not col is None:
                cols.append({
                    'key': col.key,
                    'type': str(col.type),
                    'comment': col.comment,
                    'description': col.description,
                    'nullable': col.nullable,
                    'primary_key': col.primary_key,
                    'default': str(col.default) if col.default else None,
                    'autoincrement': col.autoincrement,
                    'info':col.info,
                })
        if model_name:
            if item == model_name:    
                _maped[item] = {
                    'columns': cols,
                    'relationships': relationships,
                    'module': infos['module']
                }
        else:
            _maped[item] = {
                'columns': cols,
                'relationships': relationships,
                'module': infos['module']
            }
    return _maped

     
 
class _serviceMeta(type):
    def __new__(cls, name, bases, attrs):
        obj = super().__new__(cls, name, bases, attrs)
        # if obj.__name__!="Service":
        #     set_module_i18n(obj=obj,module_name=attrs['__module__'])
         
        return obj
# class AlchemyEncoder(json.JSONEncoder):

#     def default(self, obj):
#         if isinstance(obj.__class__, Base):
#             # an SQLAlchemy class
#             fields = {}
#             for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
#                 data = obj.__getattribute__(field)
#                 try:
#                     json.dumps(data ) # this will fail on non-encodable values, like other classes
#                     fields[field] = data
#                 except TypeError:
#                     fields[field] = None
#             # a json-encodable dict
#             return fields
#         elif isinstance(obj, (datetime, date)):
#             return obj.isoformat()
#         return json.JSONEncoder.default(self, obj)
def to_json(records:List[Base])->str:
    """
    """
    list_of_res = [row._asdict() for row in records]
    return json.dumps(list_of_res)


class ListPager:
    def __init__(self,query:Query,size:int=None,num:int=1,order_by:Optional[Tuple]=None) -> None: 
        self.query = query
        if size:
            self.page_size = size
        else:
            self.page_size = page_size 
        self.page_num = num
        self.order_by = order_by
    def page_size(self,size:int=None):
        self.page_size = size
        return self
    
    def order(self,*args)->'ListPager':
        self.query = self.query.order_by(*args)     
        return self
    def page(self,page_num=1)->'ListPager':
        self.page_num = page_num
        return self
        #return self.query.limit(self.page_size).offset(self.page_size*(page_num-1))

    def count_all(self)->int:
        return self.query.count()
    
    def page_count(self)->int:
        if not self.page_size>0:
            return 0
        import math
        return math.ceil(self.count_all()/self.page_size) 
    
    def records(self,page_size=None,page_num=None)->List[Base]:
        page_num = page_num or self.page_num or 1
        page_size = page_size or self.page_size  
        ret = self.query.limit(page_size).offset(page_size*(page_num-1)).all()
        results = [row._asdict() for row in ret]
        return results
    
class Service(metaclass=_serviceMeta):
    __all_generated = {}
    _session:Session = None
    _ = _ #the i18n traslation object ,it's will auto redirect the `app_name/locales` dir i18n configure
    @contextmanager      
    @staticmethod 
    def get_session():
        """Provide a transactional scope around a series of operations."""
        if  Service._session:
            session = Service._session
        else:
            session = Service.session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        # finally:
        #     session.close()
    @classmethod
    def session(self)->Session:
        if  Service._session:
            return Service._session 
        Service._session = Session(bind=engine) 
        return Service._session
     
    @classmethod
    def pager(self,model:Base,*args,**kwargs)->ListPager:
        """get query object with auto passed is_deleted rows"""
        pg_size = page_size
        if 'page_size' in kwargs:
            pg_size = kwargs.get('page_size')
            del kwargs['page_size']

        query = self.query(model,*args,**kwargs)
        return ListPager(query=query,size=pg_size)
    
    @classmethod
    def exists(self,model:Base,field_name:str,value:Any)->bool:
        session = self.session()
        kwargs = {field_name:value}
        try:
            q = session.query(model).filter_by(**kwargs).one()
        except sqlalchemy.exc.NoResultFound as e: 
            return False
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return True
        return not q  is None
    @classmethod
    def __check_is_deleted_param(self,model:Base,**kwargs):
        if hasattr(model,is_deleted_field):
            if not kwargs:kwargs = {}
            if not is_deleted_field in kwargs:
                kwargs[is_deleted_field] = False
            else:
                if kwargs[is_deleted_field]=='all':
                    del kwargs[is_deleted_field]
        return kwargs
    @classmethod
    def query(self,model:Base,*args,**kwargs)->Query:
        '''Get a query object with auto passed is_deleted rows'''
        session = self.session()
        kwargs = self.__check_is_deleted_param(model,**kwargs)
        query = session.query(model).filter(*args).filter_by(**kwargs)
        return query
    
    @classmethod
    def query_columns(self,*columns):
        session = self.session()
        return session.query(*columns)
    
    @classmethod
    def select(self,model:Base,*where,**kwargs)->List[Base]:
        ''' Auto pass if row has is_deleted field
            execute select statement with :where condition on :model
            :return rows of result
        '''
        kwargs = self.__check_is_deleted_param(model,**kwargs)
        stmt = select(model).where(*where).filter_by(**kwargs)
        with engine.begin() as conn:
            ret = conn.execute(stmt)
            return ret.fetchall()    
    @classmethod
    def list(self,model:Base,*args, **kwargs)->List[Base]:
        '''Auto pass is_deleted if model has is_deleted field'''
        kwargs = self.__check_is_deleted_param(model,**kwargs)
        session = self.session()  
        query = session.query(model) 
        if args:
            query = query.filter(*args)
        if kwargs:
            query = query.filter_by(**kwargs) 
        return query.all()
     
    @classmethod
    def update(self,model:Base,*where,**values)->int:
        '''
            execute update :model with :values on :model by :where
            :return rowcount
        '''
        q = self.query(model,*where) 
        cnt = 0
        for r in q:
            for field in values:
                setattr(r,field,values[field]) 
            cnt+=1
        try:
            self.session().commit()
        except Exception as e:
            self.session().rollback()
            raise e
        return cnt
    @classmethod
    def count(self,model:Base,*args,**kwargs)->int:
        ''' Auto pass if row has is_deleted field
            :return count by givened :args on :model
        '''
        kwargs = self.__check_is_deleted_param(model,**kwargs)
        
        if hasattr(model,'id'):
            
            q = self.query(func.count(model.id),*args,**kwargs)
            return q.scalar()
        else:
            return len(self.list( model,*args,**kwargs))
        
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
            session.refresh(m) 
            return m
        return None
    @classmethod
    def add_all(self,values:List['Base']):
        with self.get_session() as session: 
            session.add_all(values) 
    
    
    
    @classmethod
    def delete(self,model:Base,*args,**kwargs)->int:  
        '''Soft delete if model has is_deleted field Else real delete'''
        with self.get_session() as session:
            query = session.query(model).filter(*args).filter_by(**kwargs)
            rows = query.all()
            if hasattr(model,is_deleted_field): 
                for row in rows:
                    setattr(row,is_deleted_field,True)  
            else:
                for row in rows:
                    session.delete(row)
            cnt = len(rows)
            session.commit()
            return cnt
    @classmethod
    def restore(self,model:Union[Type,Base],*args,**kwargs):
        '''Undelete . set is_deleted field False '''
        with self.get_session() as session:
            if isinstance(model,Base):
                if hasattr(model,is_deleted_field): 
                    setattr(model,is_deleted_field,False)
                    return model
            else: 
                query = session.query(model).filter(*args).filter_by(**kwargs)
                rows = query.all()
                if hasattr(model,is_deleted_field): 
                    for row in rows:
                        setattr(row,is_deleted_field,False)   
                cnt = len(rows)
                 
                return cnt
    @classmethod
    def real_delete(self,model:Base,*args,**kwargs):
        '''Real delete rows in database'''
        with self.get_session() as session: 
            query = session.query(model).filter(*args).filter_by(**kwargs)
            cnt = 0
            for obj in query:
                session.delete(obj)
                cnt += 1
         
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
    def execute(cls,cmd:Union[str,TextClause],**kwargs):
        if not isinstance(cmd,TextClause):
            cmd = text(cmd)
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

 
def sanitize_path(path):
    # 匹配非法字符
    illegal_chars = r'[\\/:\*\?"<>\|]'
    # 将非法字符替换为下划线
    sanitized_path = re.sub(illegal_chars, '_', path)
    return sanitized_path

def check_migration(engine:Engine,uri,alembic_ini,upgrade=None): 
    if os.path.isabs(alembic_ini)==False:
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
        #ensure not have some versions on db
        _tb = 'alembic_version'
        _migration_files = os.listdir(reversions_dir)
        has_migration = False
        if len(_migration_files)>0:
            for f in _migration_files:
                if f.endswith('.py'):
                    has_migration = True
                    break
        if not has_migration:
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"delete from {_tb}"))
            except:
                pass
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise InitDbError(e.args)
    _update_uri_to_ini()
    #  
    from typing import TextIO
    io = TextIO()
    log_level =_log.level

    alembic_cfg = Config(alembic_ini,stdout=io)    
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
    io.close()
    _log.level = log_level
def _test_connection():
    #test connect
    try:
        with engine.connect() as conn:
            _log.disabled = False
            _log.debug(_('database connection successed:')) 

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
        if not os.path.isabs(db_directory):
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
