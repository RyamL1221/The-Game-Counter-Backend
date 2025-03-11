from marshmallow import Schema, fields

class DataSchema(Schema):
    auth_token = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
