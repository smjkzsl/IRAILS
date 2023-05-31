
from irails.database import Service, Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.sqla_oauth2 import (
    create_bearer_token_validator,
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
)
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6750 import BearerTokenValidator
import bcrypt
import os
from irails.core import application

from system_admin.models import User,OAuth2Token



class OAuth2Service(Service):
    @classmethod
    def create_user_token(self,user_id: str, token: str):
        
        user = self.query(User).get(user_id)
        if not user:
            return None

        oauth2_token = OAuth2Token(**token)
        oauth2_token.user_id = user.id
        self.add(oauth2_token) 
        return oauth2_token