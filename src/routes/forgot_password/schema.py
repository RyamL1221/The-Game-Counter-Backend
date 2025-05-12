from marshmallow import Schema, fields

class DataSchema(Schema):
    email = fields.Email(required=True)
    security_answer = fields.String(required=True)
    new_password = fields.String(required=True)
    confirm_password = fields.String(required=True)