from marshmallow import Schema, fields

class DataSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    security_question = fields.String(required=True)
    security_answer = fields.String(required=True)
