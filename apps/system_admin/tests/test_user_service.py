from irails.unit_test import *
from system_admin.services import UserService
from system_admin.models.user import User,Role
from irails._i18n import _

class TestUserService(ServiceTest):
      def test_user_service(self):
         service: UserService = UserService()
            # 删除实例
         service.real_delete(User)
         service.real_delete(Role)
            # 创建用户实例并添加到数据库
         user = User()
         user.name = "bruce"
         user.fullname = "bruce chou"
         user.age = 18
         service.add(user)
         self.assertGreater(user.id, 0)
         self.assertTrue(User.check_password(user, "bruce"))
            # 创建另一个用户实例并添加到数据库
         user1 = service.add(User, name="alice", fullname='alice jose', age=22)
         self.assertTrue(user1.id)
            # 创建角色实例并添加到数据库
         role: Role = service.add(Role, name="admin")
         self.assertTrue(role.id)
            # 将用户添加到角色中
         role.users.append(user)
         role.users.append(user1)
         service.flush(role)
          
         service.add(User,name="root",domain="system",age=40)
         root_user:User = service.query(User,User.name=='root').one()
         self.assertTrue(root_user)
         root_user.roles.append(role)
         service.flush()
        