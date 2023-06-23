from marshmallow import Schema, fields


class PlainBetsSchema(Schema):
    id = fields.Int(dump_only = True)
    match_id = fields.Str(required=True)
    goal1 = fields.Int(required=True)
    goal2 = fields.Int(required=True)
    done = fields.Str(required = True)

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

'''
Users
'''

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

'''
Bets
'''

class BetsSchema(PlainBetsSchema):
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)

# class BetsUpdateSchema(Schema):
#     match_id = fields.Str(required=True)
#     goal1 = fields.Int(required=True)
#     goal2 = fields.Int(required=True)
#     user_id = fields.Int(required=True, load_only=True)
#     done = fields.Str(required = True)
#     user = fields.Nested(PlainUserSchema(), dump_only=True)

'''
Matches
'''

class MatchesSchema(Schema):
    id = fields.Int(dump_only = True)
    match_id = fields.Str(dump_only = True)
    goal1 = fields.Int(dump_only = True)
    goal2 = fields.Int(dump_only = True)

'''
Groups
'''

class CreateGroupsSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(PlainUserSchema(), dump_only = True)

class GetGroupsSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(dump_only=True)
    user = fields.List(fields.Nested(PlainUserSchema()), dump_only = True)

class JoinGroupsSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(dump_only=True)
    user_id = fields.Str(required=True, load_only=True)
    user = fields.List(fields.Nested(PlainUserSchema()), dump_only = True)



    

