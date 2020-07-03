from flask_marshmallow import Marshmallow
import app


ma = Marshmallow(app)

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('uuid', 'email', 'username', 'name', 'created_date', 'archived')
        _links = ma.Hyperlinks(
            {'self': ma.URLFor('get_user', uuid='<uuid>')}
        )

class FollowSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('originating_id', 'label', 'target_id', 'created_date')

class GroupSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('uuid', 'name', 'created_date')

class GroupMembershipSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('member_id', 'label', 'group_id', 'created_date')
