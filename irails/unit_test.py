
import unittest
from .core import generate_mvc_app
from ._i18n import set_module_i18n

class _BaseUnitTest(unittest.TestCase):
    application = generate_mvc_app()
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
    def __init_subclass__(cls,*args,**kwargs) -> None:  
        set_module_i18n(cls,cls.__module__)
        super().__init_subclass__(*args,**kwargs)    
class ControllerTest(_BaseUnitTest):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from fastapi.testclient import TestClient 
        self.client = TestClient(app=self.application)
        
    pass

class ServiceTest(_BaseUnitTest):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from irails.database import Service,engine,Session
        self.service = Service
        self.engine = engine
        if not hasattr(ServiceTest,'session'):
            ServiceTest.session = Session(bind=self.engine)
        
    pass