"""
"""
from typing import Type,TYPE_CHECKING, Any, Callable, get_type_hints 
from fastapi import FastAPI,APIRouter  
from .controller_utils import (TEMPLATE_PATH_KEY, VER_KEY, ControllerBase,
                               _get_leaf_controllers,
                               _register_controller_to_router, _route_method)

 
from ._i18n import _

class InferringRouter(APIRouter):
    """
    Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
    """
    pass
    # if not TYPE_CHECKING:  # pragma: no branch

    #     def add_api_route(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
    #         if kwargs.get("response_model") is None:
    #             kwargs["response_model"] = get_type_hints(endpoint).get("return")
    #         return super().add_api_route(path, endpoint, **kwargs)
        
def register_controllers_to_app(app: FastAPI,
                                controller_base: Type[ControllerBase]) -> None:
    """
    Registers all the api routes inside child controllers of the base
    controller.


    Args:
      app: FastAPI: root FastAPI app
      controller_base: Type[ControllerBase]: base controller class generated by
      create_controller function

    Returns:
    None
    """
    router = InferringRouter()

    controllers = _get_leaf_controllers(controller_base)

    for ctrl in controllers:
        _register_controller_to_router(router, ctrl)

    app.include_router(router)
    return router


def create_controller(template_path_prefix: str = "", version: str = "") -> Type[ControllerBase]:
    """
    Create a base controller that can be used as a parent controller for other
    Controllers. Allows the ability to add a path prefix and to version the
    api.

    Args:
      template_path_prefix: str: path prefix for all the controllers. You can
      use template variables
      `version` and `controller` to replace the version 
      version: str:

    Returns:
    Type[ControllerBase]: a class that can be used as a base for other
    controllers.
    """

    class GeneratedController(ControllerBase):
        """ """

        pass

    setattr(GeneratedController, TEMPLATE_PATH_KEY, template_path_prefix)
    setattr(GeneratedController, VER_KEY, version)

    return GeneratedController


class MvcRouter: 
    """ """
    @classmethod
    def init(cls,app):
        cls.app = app

    @staticmethod
    def http(path,methods=['GET'],*args,**kwargs):
        return _route_method(path,method=methods,*args,**kwargs)
    @staticmethod
    def get(path: str, *args, **kwargs): 
        """if path eq application._public_auth_url,the auth agr must set to 'none' """
        if MvcRouter.app and path == MvcRouter.app.public_auth_url:
            if 'auth' in kwargs and kwargs['auth']!='none':
                raise RuntimeError(_('the public auth path must set to "none" on auth arguments')) 
            elif not 'auth' in kwargs:
                 kwargs['auth'] = 'none'
        return _route_method(path, "get", *args, **kwargs)

    @staticmethod
    def post(path: str, *args, **kwargs): 
        return _route_method(path, "post", *args, **kwargs)

    @staticmethod
    def put(path: str, *args, **kwargs): 
        return _route_method(path, "put", *args, **kwargs)

    @staticmethod
    def patch(path: str, *args, **kwargs): 
        return _route_method(path, "patch", *args, **kwargs)

    @staticmethod
    def delete(path: str, *args, **kwargs): 
        return _route_method(path, "delete", *args, **kwargs)

    @staticmethod
    def head(path: str, *args, **kwargs): 
        return _route_method(path, "head", *args, **kwargs)

    @staticmethod
    def options(path: str, *args, **kwargs): 
        return _route_method(path, "options", *args, **kwargs)

    @staticmethod
    def trace(path: str, *args, **kwargs): 
        return _route_method(path, "trace", *args, **kwargs)
    
    @staticmethod
    def websocket(path: str, *args, **kwargs): 
        return _route_method(path, "websocket", *args, **kwargs)
