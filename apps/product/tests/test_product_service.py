from irails.unit_test import *
from irails.apps.product.services import ProductService
from irails.apps.product.models import Product

class TestProductService(ServiceTest):
    
    def test_product_service(self):
        service:ProductService = ProductService()
        obj = Product()
                
                
        service.add(obj)
        id = obj.id
        query_obj = service.get(Product,id)
        self.assertEqual(obj,query_obj)