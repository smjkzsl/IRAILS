from fastapi import WebSocketDisconnect,WebSocket
from .core import (
    api_router as route, 
    api,
    Response,
    Request, 
    application,
    generate_mvc_app,
    
    )
from .base_controller import BaseController
 
from fastapi import Form,UploadFile,File
from . import apps

__version__="1.6.5"
