from marshmallow import Schema, fields

class DataSchema(Schema):
    count = fields.Integer(required=True)
