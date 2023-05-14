from irails.unit_test import *
from system.services import UserService
from system.models.user import User

class TestUserService(ServiceTest):
    
    def test_user_service(self):
        service:UserService = UserService()
        obj = User()
                
                
            
        obj.name = "new_value"
        
                
                
            
        obj.fullname = "new_value"
        
                
                
            
        obj.age = "new_value"
        obj = service.add(obj)
        id = obj.id
        query_obj = service.get(id)
        self.assertEqual(obj,query_obj)