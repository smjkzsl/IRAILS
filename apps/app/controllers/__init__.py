from .test_controller import *

@application.on_event("startup")
def startup():   
    application.policy('kefu','system','/chatgpt', 'GET', authorize=True)
  