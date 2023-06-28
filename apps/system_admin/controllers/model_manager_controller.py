# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
from irails.database import get_meta

@route('/{app}/{controller}',auth="user")
class ModelManagerController(BaseController):

  
    
    @api.get("/model_meta")
    def model_meta(self,model_name:str=""):
        """
        :title ModelMeta
        """
        return get_meta(model_name)