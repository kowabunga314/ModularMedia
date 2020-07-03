# from app import create_app
from apispec import APISpec
import json

# Create spec
spec = APISpec(
    openapi_version=3.0,
    title='Modular Media API',
    version='0.1.1',
    info=dict(
        description='You know, for devs'
    ),
    # plugins=[
    #     'apispec.ext.flask',
    #     'apispec.ext.marshmallow'
    # ]
)

# Reference your schemas definitions
from app.modules.user.schema import UserSchema, FollowSchema, GroupSchema, GroupMembershipSchema

spec.definition('User', schema=UserSchema)
spec.definition('Follow', schema=FollowSchema)
spec.definition('Group', schema=GroupSchema)
spec.definition('GroupMembership', schema=GroupMembershipSchema)

# Now, reference your routes.
from app.modules.user.app import my_route

# We need a working context for apispec introspection.
app = create_app()

with app.test_request_context():
    spec.add_path(view=my_route)
    # ...

# We're good to go! Save this to a file for now.
with open('swagger.json', 'w') as f:
    json.dump(spec.to_dict(), f)