import json
from enum import Enum
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, validate
from marshmallow_enum import EnumField
import pickle


class RepTag(str,Enum):  # reply tag
    LOGIN_SUCCESS = 'LSS'
    SIGNUP_SUCCESS = 'SSS'
    ONLINE = 'ONL'
    OFFLINE = 'OFF'
    SESSION_REJECT = 'SRJ'
    SESSION_ACCEPT = 'SAT'
class ReqTag(str,Enum): # request tag
    LOGIN = 'LIN'
    LOGOUT = 'LUT'
    SIGNUP = 'SIN'
    SESSION_OPEN = 'SOP'
    SESSION_CLOSE = 'SCL'
    SESSION_REJECT = 'SRJ'
    SESSION_ACCEPT = 'SAT'
    DISCONNECT = 'DIS'
class RequestSchema(Schema):
    type = EnumField(ReqTag, by_value=True)

class ClientSchema(Schema):
    type = EnumField(ReqTag, by_value=True)
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
    nickname = fields.Str(required=True)
    @validates("username")
    def validateSignup(self,value):
        with open('HMap.json', 'r') as file:
            hashmap = json.load(file)
        if value in hashmap:
            raise ValidationError('Username already in use')
class LoginAuthenSchema(ClientSchema):
    @validates_schema
    def authen(self, data, **kwargs):
        with open('HMap.json', 'r') as file:
            hashmap = json.load(file)
        if data['username'] not in hashmap:
            raise ValidationError('Wrong username')
        with open("Users.json") as openfile:
            users = json.load(openfile)
        if users[hashmap[data['username']]]['password'] != data['password']:
            raise ValidationError('Wrong password')

class SessionSchema(RequestSchema):
    destID = fields.Int(required=True)
    ip = fields.IP(required=True)
    port = fields.Int(required=True)
    class Meta:
        strict = True

class BriefSessionSchema(RequestSchema):
    destID = fields.Int(required=True)
    class Meta:
        strict = True