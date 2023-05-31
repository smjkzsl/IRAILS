from irails.database import Base,Column,Integer,String,relationship,Text,ForeignKey,table_prefix
from .user import User
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     password = Column(String)

class OAuth2Client(Base):
    __tablename__ = f'{table_prefix}oauth2_clients'
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, unique=True, index=True)
    client_secret = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="clients")
    _redirect_uris = Column(Text)
    _default_scopes = Column(Text)

    @property
    def client_id(self):
        return self.client_name

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class OAuth2Token(Base):
    __tablename__ = f'{table_prefix}oauth2_tokens'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(48))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="tokens")
    token_type = Column(String(40))
    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    expires_in = Column(Integer)
    scope = Column(Text)
    revoked = Column(Integer)

User.clients = relationship("OAuth2Client", order_by=OAuth2Client.id, back_populates="user")
User.tokens = relationship("OAuth2Token", order_by=OAuth2Token.id, back_populates="user")

