from irails.unit_test import *

class test_sys_admin(ControllerTest):
    
    def test_index(self):
        self.assertEqual(self.client.get("/sys_admin/index").status_code,200)
    def test_index1(self):
        self.assertIn(self.client.get("/sys_admin/index").text,'view')