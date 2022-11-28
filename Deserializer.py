import json
from enum import Enum
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from marshmallow_enum import EnumField
from utils import hashmap
import pickle


class ReqTag(Enum): # request tag
    LOGIN = 'LOGIN'
    SIGNUP = 'SIGNUP'
    SESSION_OPEN = 'SOP'
    SESSION_CLOSE = 'SCL'
class ClientSchema(Schema):
    type = EnumField(ReqTag)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    class Meta:
        strict = True
    @validates("type")
    def validateType(self,value):
        if value not in [ReqTag.LOGIN,
                         ReqTag.SIGNUP]:
            raise ValidationError('Please login or signup')
class SignUpSchema(ClientSchema):
    @validates("username")
    def validateSignup(self,value):
        if value in hashmap:
            raise ValidationError('Username already in use')
class LoginAuthenSchema(ClientSchema):
    @validates_schema
    def authen(self, data, **kwargs):
        if data['username'] not in hashmap:
            raise ValidationError('Wrong username')
        with open("Users.json") as openfile:
            users = json.load(openfile)
        if users[hashmap[data['username']]]['password'] != data['password']:
            raise ValidationError('Wrong password')

class SessionSchema(Schema):

class
