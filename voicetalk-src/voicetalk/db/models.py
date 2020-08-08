from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, DefaultClause, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Boolean

base = declarative_base()


class User(base):
    __tablename__ = 'User'

    id = Column('id', Integer, autoincrement=True, primary_key=True)
    username = Column('username', String(255), nullable=False, unique=True)
    password = Column('password', String(255), nullable=False)
    is_active = Column('is_active', Boolean, server_default=DefaultClause('1'))
    is_anonymous = Column('is_anonymous', Boolean, server_default=DefaultClause('0'))
    is_authenticated = Column('is_authenticated', Boolean,
                              server_default=DefaultClause('1'))

    access_tokens = relationship('AccessToken', back_populates='user',
                                 cascade='all, delete-orphan')

    refresh_tokens = relationship('RefreshToken', back_populates='user',
                                  cascade='all, delete-orphan')

    authorization_codes = relationship('AuthorizationCode', back_populates='user',
                                       cascade='all, delete-orphan')

    def get_id(self):
        return self.id


class AccessToken(base):
    __tablename__ = 'AccessToken'
    __table_args__ = (ForeignKeyConstraint(['u_id'], ['User.id'],
                                           onupdate='CASCADE', ondelete='CASCADE'),
                      ForeignKeyConstraint(['refresh_token_id'],
                                           ['RefreshToken.id'],
                                           onupdate='CASCADE',
                                           ondelete='CASCADE'),
                      UniqueConstraint('token'))

    id = Column('id', Integer, autoincrement=True, primary_key=True)
    expires_at = Column('expires_at', Integer, nullable=False)
    refresh_token_id = Column('refresh_token_id', Integer, nullable=False)
    token = Column('token', String(255), nullable=False)
    u_id = Column('u_id', Integer, nullable=False)

    refresh_token = relationship('RefreshToken', back_populates='access_token')
    user = relationship('User', back_populates='access_tokens')


class RefreshToken(base):
    __tablename__ = 'RefreshToken'
    __table_args__ = (ForeignKeyConstraint(['u_id'], ['User.id'],
                                           onupdate='CASCADE', ondelete='CASCADE'),
                      UniqueConstraint('token'))

    id = Column('id', Integer, autoincrement=True, primary_key=True)
    token = Column('token', String(255), nullable=False)
    u_id = Column('u_id', Integer, nullable=False)

    # Since it's one-to-one relationship with AccessToken, we need to set uselist to False
    # So that the access_token is an attribute instead of a list
    access_token = relationship('AccessToken', back_populates='refresh_token',
                                cascade='all ,delete-orphan', uselist=False)
    user = relationship('User', back_populates='refresh_tokens')


class AuthorizationCode(base):
    __tablename__ = 'AuthorizationCode'
    __table_args__ = (ForeignKeyConstraint(['u_id'], ['User.id'],
                                           onupdate='CASCADE', ondelete='CASCADE'),
                      UniqueConstraint('code'))

    id = Column('id', Integer, autoincrement=True, primary_key=True)
    code = Column('code', String(255), nullable=False)
    expires_at = Column('expires_at', Integer, nullable=False)
    redirect_uri = Column('redirect_uri', String(255), nullable=False)
    u_id = Column('u_id', Integer, nullable=False)

    user = relationship('User', back_populates='authorization_codes')
