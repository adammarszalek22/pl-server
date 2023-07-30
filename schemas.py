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

class RegisterSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    password2 = fields.Str(required=True, load_only=True)

'''
Users
'''

class GroupUserSchema(PlainUserSchema):
    points = fields.Int()
    position = fields.Int()
    three_pointers = fields.Int()
    one_pointers = fields.Int()

class UserSchema(PlainUserSchema):
    points = fields.Int()
    position = fields.Int()
    three_pointers = fields.Int()
    one_pointers = fields.Int()
    bets = fields.List(fields.Nested(PlainBetsSchema(), dump_only=True))

class UserSchemaByPos(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)

    points = fields.Int(dump_only=True)
    position = fields.Int(required=True)
    three_pointers = fields.Int(dump_only=True)
    one_pointers = fields.Int(dump_only=True)

class FirstTenSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)

    points = fields.Int(dump_only=True)
    position = fields.Int(dump_only=True)
    three_pointers = fields.Int(dump_only=True)
    one_pointers = fields.Int(dump_only=True)

class UsernameSchema(Schema):
    username = fields.Str(required=True)
    points = fields.Int(dump_only=True)
    position = fields.Int(dump_only=True)
    three_pointers = fields.Int(dump_only=True)
    one_pointers = fields.Int(dump_only=True)

class AllUserSchema(PlainUserSchema):
    points = fields.Int()
    position = fields.Int()
    three_pointers = fields.Int()
    one_pointers = fields.Int()



'''
Bets
'''

class BetsSchema(PlainBetsSchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)

class MultipleUpdateBetsSchema(Schema):
    id = fields.Int(dump_only = True)
    match_id = fields.List(fields.Str(), required=True)
    goal1 = fields.List(fields.Int(), required=True)
    goal2 = fields.List(fields.Int(), required=True)
    user = fields.Nested(PlainUserSchema(), dump_only=True)

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
    user = fields.List(fields.Nested(PlainUserSchema()), dump_only = True)

class GetGroupsSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(dump_only=True)
    admin_id = fields.Int(dump_only=True)
    positions = fields.Str(dump_only=True)
    user = fields.List(fields.Nested(GroupUserSchema()), dump_only = True)

class JoinGroupsSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(dump_only=True)
    user = fields.List(fields.Nested(PlainUserSchema()), dump_only = True)

class DeleteGroupSchema(Schema):
    id = fields.Int(required=True, load_only=True)

class DeleteUserFromGroup(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)

class MyGroupSchema(Schema):
    user_id = fields.Int(required=True)
    

'''
ADMIN
'''

class UserUpdateSchema(Schema):
    user_id = fields.Int(required=True)
    points = fields.Int(required=True)
    three_pointers = fields.Int(required=True)
    one_pointers = fields.Int(required=True)
    bets = fields.List(fields.Nested(PlainBetsSchema(), dump_only=True))


    

