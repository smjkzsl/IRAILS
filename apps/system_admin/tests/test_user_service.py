from irails.unit_test import *
from system_admin.services import UserService
from system_admin.models.user import User,Role

class TestUserService(ServiceTest):
    
    def test_user_service(self):
        service:UserService = UserService()
        service.delete(User)
        service.delete(Role)
        user = User() 
        user.name = "bruce" 
        user.fullname = "bruce chou" 
        user.age = 18 
        service.add(user)
        self.assertGreater(user.id,0)
        
        #new one again
        user1 = service.add(User,name="alice",fullname='alice jose',age=22)
        self.assert_(user1.id)

        role:Role = service.add(Role,name="admin")
        self.assert_(role.id)

        role.users.append(user)
        role.users.append(user1)
        service.flush(role)
        
        users = service.list(User)
        self.assertEqual(len(users),2)

        self.assertEqual(users[0].roles[0],role)