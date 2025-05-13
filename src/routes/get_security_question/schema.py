from marshmallow import Schema, fields

class DataSchema(Schema):
    email = fields.Email(required=True)