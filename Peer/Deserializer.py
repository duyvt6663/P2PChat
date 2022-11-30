import json
from enum import Enum
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, validate
from marshmallow_enum import EnumField
import pickle


class RepTag(str,Enum): # reply tag
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