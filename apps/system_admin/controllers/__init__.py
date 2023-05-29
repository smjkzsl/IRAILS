from irails.core import application
    
from . import admin_controller
from . import user_controller

@application.on_event("startup")
def startup(): 
 
    #p, admin, domain1, data1, read 
    application.policy('admin','system','/system_admin/admin/*', '(GET)|(POST)', authorize=True) 
    application.policy('admin','system','/system_admin/user/*', '(GET)|(POST)', authorize=True)  
    #g, alice, admin, domain1 
    application.grouping('bruce','admin','system', authorize=True)
    application.grouping('root','admin','system', authorize=True)
