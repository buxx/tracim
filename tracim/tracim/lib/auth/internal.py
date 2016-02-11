# -*- coding: utf-8 -*-
from sqlalchemy import and_
from tg.configuration.auth import TGAuthMetadata

from tracim.lib.auth.base import Auth
from tracim.model import DBSession, User


class InternalAuth(Auth):

    name = 'internal'

    def wrap_config(self):
        super().wrap_config()

        self._config.sa_auth.user_class = User
        self._config.auth_backend = 'sqlalchemy'
        self._config.sa_auth.dbsession = DBSession
        self._config.sa_auth.authmetadata = InternalApplicationAuthMetadata(self._config.sa_auth)


class InternalApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        user = self.sa_auth.dbsession.query(self.sa_auth.user_class).filter(and_(
            self.sa_auth.user_class.is_active == True,
            self.sa_auth.user_class.email == identity['login']
        )).first()

        if user and user.validate_password(identity['password']):
            return identity['login']

    def get_user(self, identity, userid):
        return self.sa_auth.dbsession.query(self.sa_auth.user_class).filter(
            and_(self.sa_auth.user_class.is_active == True, self.sa_auth.user_class.email == userid)).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]