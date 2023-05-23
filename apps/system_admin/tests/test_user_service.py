from irails.unit_test import *
from system_admin.services import UserService
from system_admin.models.user import User,Role
from irails._i18n import _

class TestUserService(ServiceTest):
    
    def test_user_service(self):
        service:UserService = UserService()
        service.real_delete(User)
        service.real_delete(Role)
        user = User() 
        user.name = "bruce" 
        user.fullname = "bruce chou" 
        user.age = 18 
        service.add(user)
        self.assertGreater(user.id,0)
        self.assertTrue(User.check_password(user,"bruce"))
        #new one again
        user1 = service.add(User,name="alice",fullname='alice jose',age=22)
        self.assertTrue(user1.id)

        role:Role = service.add(Role,name="admin")
        self.assertTrue(role.id)

        role.users.append(user)
        role.users.append(user1)
        service.flush(role)
        
        users = service.list(User)
        self.assertEqual(len(users),2)

        self.assertEqual(users[0].roles[0],role)

        #test query
        users = service.query_user(User.name.like("bru%")).all()
        self.assertEqual(len(users),1)
        self.assertEqual(users[0].name,'bruce')
        for u in users:
            print(u)
        print("Translation Test:",_("id"))
        _bulks = []
        for i in range(18,28):
            _bulks.append(User(name=f"rebot{i}",
                               fullname=f"test rebot{i}",
                               age=i+10,password="pwd123456"
                               ))
        service.bulk_add(_bulks)
        self.assertTrue(User.check_password(_bulks[0],'pwd123456'))
        self.assertEqual(service.count(User),12)
        self.assertEqual(service.count(User,User.age>30),7)
        self.assertEqual(service.count(User,User.name.like('rebot%')),10)

        
        c=service.update(User,User.age>18,User.name.like('rebot%'), name="test")
        self.assertEqual(c,10)
        service.session().commit()
        self.assertEqual(service.count(User,User.name.like('test')),10)

        self.assertEqual(service.count(User,User.age==18),1)

        #test select
        rows = service.select(User,User.age>30)
        self.assertEqual(len(rows),7)

        #test delete
        service.delete(User,User.age<30)
        self.assertEqual(service.count(User),8)
