
import unittest
from .core import generate_mvc_app
from ._i18n import set_module_i18n

class _BaseUnitTest(unittest.TestCase):
    
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
    def __init_subclass__(cls,*args,**kwargs) -> None:  
        set_module_i18n(cls,cls.__module__)
        super().__init_subclass__(*args,**kwargs)    
class ControllerTest(_BaseUnitTest):
    
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        if not hasattr(_BaseUnitTest,'application'):
            _BaseUnitTest.application = generate_mvc_app()
        from fastapi.testclient import TestClient 
        self.client = TestClient(app=self.application)
        
    pass

class ServiceTest(_BaseUnitTest):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from .config import config
        from ._loader import _load_apps
        from irails.database import Service,engine,Session,init_database
        
         
        # _load_apps()
        if not hasattr(_BaseUnitTest,'engine'):
            db_cfg = config.get("database")
            db_uri = db_cfg.get("uri")
            _BaseUnitTest.engine = init_database(db_uri,debug=True,cfg = db_cfg)
        self.service = Service
        self.engine = engine
        if not hasattr(ServiceTest,'session'):
            ServiceTest.session = Session(bind=self.engine)
        
    pass