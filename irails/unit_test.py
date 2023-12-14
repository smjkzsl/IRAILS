
import unittest


from .core import generate_mvc_app
# from ._i18n import set_module_i18n

class _BaseUnitTest(unittest.TestCase):
    
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
    def __init_subclass__(cls,*args,**kwargs) -> None:  
        super().__init_subclass__(*args,**kwargs)    
        # if not cls.__name__ in ['ControllerTest','ServiceTest']:
        #     set_module_i18n(cls,cls.__module__)
        
class ControllerTest(_BaseUnitTest):
    
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        if not hasattr(_BaseUnitTest,'application'):
            _BaseUnitTest.application = generate_mvc_app('testmode')
        from fastapi.testclient import TestClient 
        self.client = TestClient(app=_BaseUnitTest.application)
        
    pass

class ServiceTest(_BaseUnitTest):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from .config import config
        from ._loader import collect_apps
        from irails.database import Service,engine,Session,init_database
        from irails.database import check_migration
        from irails.core import check_init_auth
        # _load_apps()
        if not hasattr(ServiceTest,'engine'):
            db_cfg = config.get("database")
            db_uri = db_cfg.get("uri")
            alembic_ini = db_cfg.get("alembic_ini")
            ServiceTest.engine = init_database(db_uri,debug=True,cfg = db_cfg)
            check_init_auth(db_cfg)
            #test mode do not run migrate
            # if ServiceTest.engine:
            #     check_migration(engine=ServiceTest.engine,uri= db_uri,alembic_ini= alembic_ini )
            self.service = Service()
     