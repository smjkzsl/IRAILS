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
            # 查询用户列表并验证
         users = service.list(User)
         self.assertEqual(len(users), 2)
         self.assertEqual(users[0].roles[0], role)
            # 测试查询功能
         users = service.query(User,User.name.like("bru%")).all()
         self.assertEqual(len(users), 1)
         self.assertEqual(users[0].name, 'bruce')
         for u in users:
               print(u)
         print("Translation Test:", _("id"))
            # 批量创建用户并添加到数据库
         _bulks = []
         for i in range(18, 28):
               _bulks.append(User(name=f"rebot{i}",
                                 fullname=f"rebot user {i}",
                                 age=i + 10, password="pwd123456",
                                 roles=[role]
                                 ))
         service.add_all(_bulks)
         self.assertTrue(User.check_password(_bulks[0], 'pwd123456'))
         self.assertEqual(service.count(User), 12)
         self.assertEqual(service.count(User, User.age > 30), 7)
         self.assertEqual(service.count(User, User.name.like('rebot%')), 10)
            # 更新用户信息
         c = service.update(User, User.age > 18, User.name.like('rebot%'), name='test')
         self.assertEqual(c, 10)
         self.assertEqual(service.count(User, User.name.like('test')), 10)
         self.assertEqual(service.count(User, User.age == 18), 1)
            # 查询并验证
         rows = service.select(User, User.age > 30)
         self.assertEqual(len(rows), 7)
            # 删除满足条件的用户
         service.delete(User, User.age < 30)
         self.assertEqual(service.count(User), 8)
         service.restore(service.get(User,1))
         self.assertEqual(service.count(User), 9)
      def test_pager(self):
         import math
         page_size = 3
         page_num = 1
         service: UserService = UserService()
         q = service.query(User).order_by(User.name)
         cnt = q.count()
         self.assertEqual(3, math.ceil(cnt / page_size))
         q = q.limit(page_size).offset(page_size * (page_num - 1))
         rows = q.all()
         self.assertEqual(len(rows), page_size)
      def test_list_pager(self):
         service: UserService = UserService()
         pager = service.pager(User,is_deleted="all")
         self.assertEqual(pager.page_count(), 1, '总页数')
         self.assertEqual(pager.count_all(), 12, '总行数')
         rows = pager.get(1)
         self.assertEqual(len(rows), 12, '当前页行数')

         rows = pager.order(User.age.desc()).get(1)
         self.assertEqual(rows[0].age,37)

         rows = pager.order(User.age.asc()).get()
         self.assertEqual(rows[0].age,18)
      def test_exists(self):
         service = UserService()
         self.assertTrue(service.exists(User,'name','bruce'))
         self.assertFalse(service.exists(User,'name','bbb'))

        