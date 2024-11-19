from marshmallow import Schema, fields

class DataSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
