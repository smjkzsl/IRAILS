
import unittest
class ControllerTest(unittest.TestCase):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from fastapi.testclient import TestClient
        from irails.core import generate_mvc_app,application
        if not hasattr(ControllerTest,'application'):
            generate_mvc_app()
            ControllerTest.application = application
        self.client = TestClient(app=self.application)
        
    pass

class ServiceTest(unittest.TestCase):
    def __init__(self,*args,**kwargv) -> None:
        super().__init__(*args,**kwargv)
        from irails.database import Service,engine
        self.service = Service
        self.engine = engine
    pass