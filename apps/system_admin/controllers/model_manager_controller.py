# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
from irails import database  

@route('/{app}/{controller}',auth="user")
class ModelManagerController(BaseController):  
    
    @api.get("/model_meta")
    def model_meta(self,model_name:str=""):
        """
        :title Model0Meta
        """
        return database.get_meta(model_name)
    
    def _get_request_model(self):
        model_name = self.params('model')
        module_name = self.params("module")
        model = database.get_model(model_name,module_name)
        return model
    
    @api.get("/model_data")
    def model_data(self):
        """
        :nav false
        """
        import json
         
        page_size = int( self.params('page_size',20) )
        page_num = int( self.params('page_num',1) )
        order_name = self.params('order')
        params = self.params("params")
        query_params = {}
        if params:
            query_params.update(json.loads(params))
        is_deleted = self.params(database.is_deleted_field)
        if is_deleted: # is_deleted = 'all' ?
            query_params.update({database.is_deleted_field:is_deleted})    
        from sqlalchemy import or_,and_
        model = self._get_request_model()
        if model:
            columns = model._general_columns()
            query = database.Service.query_columns(*columns)
            query = query.filter_by(**query_params)
            pager = database.ListPager(query,page_size)
            # pager = database.Service.pager(model,*columns, **query_params)
            if order_name:
                _order_list = order_name.split(',') 
                _p_order = tuple(_o for _o in _order_list) 
                pager = pager.order(*_p_order)
            if page_num:
                pager = pager.page(page_num)
            records = pager.records()
            total = pager.count_all()
            ret = {'data':records,'currentPage':page_num,'pageSize':page_size,'total':total}
            return self.json(ret)
        else:
            return self.json({},"Failed",404)
        
    @api.post("/model")
    def model_create(self):
        model = self._get_request_model()
        if model:
            data = self.params("data")
            if data:
                try:
                    import json
                    data = json.loads(data)
                    result = database.Service.add(model,**data)
                    if result:
                        return self.json([result])
                except Exception as e:
                    return self.json(e.args,"Failed",500)
        else:
            return self.json({},"Failed",404)
    
    @api.delete("/model")
    def model_delete(self):
        """
        delete a model
        """
        model  = self._get_request_model()
        if model:
            id = int(self.params("id"))
            if id:
                record = database.Service.get(model,id)
                if record:
                    if hasattr(record,'id'):
                        ret = database.Service.delete(model,id=record.id)
                        return self.json(ret)
                 
                    
        return self.json({},"Failed",404)
      
            
    @api.put("/model")
    def update_model(self):
        """
        update record
        """
        model = self._get_request_model()
        if model:
            data = self.params("data")
            id = int(self.params("id"))
            if id and data:
                record = database.Service.get(model,id) 
                if not record:
                    return self.json("Not Found!","Failed",404)
                import json
                try:
                    data = json.loads(data)
                    for field in data:
                        if 'id'==field :
                            continue
                        if hasattr(record,field):
                            setattr(record,field,data[field])
                        else:
                            return self.json("Attribute Not Found","Failed",404)
                    database.Service.flush(record)
                    return self.json("Success!")
                
                except Exception as e:
                    return self.json(e.args,"Failed",500)
                

        return self.json("Not Found!","Failed",404)
    
    