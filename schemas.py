from marshmallow import Schema, fields

class PlainBetsSchema(Schema):
    id = fields.Int(dump_only = True)
    match_id = fields.Str(required=True)
    goal1 = fields.Int()
    goal2 = fields.Int()

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserSchema(PlainUserSchema):
    points = fields.Int()
    position = fields.Int()
    three_pointers = fields.Int()
    one_pointers = fields.Int()
    bets = fields.List(fields.Nested(PlainBetsSchema(), dump_only=True))

class AllUserSchema(PlainUserSchema):
    points = fields.Int()
    position = fields.Int()
    three_pointers = fields.Int()
    one_pointers = fields.Int()

class UserUpdateSchema(Schema):
    points = fields.Int(required=True)
    position = fields.Int(required=True)
    three_pointers = fields.Int(required=True)
    one_pointers = fields.Int(required=True)

class BetsSchema(PlainBetsSchema):
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)

class BetsUpdateSchema(Schema):
    #id = fields.Int(dump_only=True)
    match_id = fields.Str(required=True)
    goal1 = fields.Int(required=True)
    goal2 = fields.Int(required=True)
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)




    

