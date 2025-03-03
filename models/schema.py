from marshmallow import Schema, fields

class DataSchema(Schema):
    auth_token = fields.String(required=True)
    email = fields.Email(required=True)
