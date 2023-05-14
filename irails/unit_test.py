
import unittest
from .core import generate_mvc_app
class _BaseUnitTest(unittest.TestCase):
    application = generate_mvc_app()
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        
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