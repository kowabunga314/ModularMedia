from flask_marshmallow import Marshmallow
import app


ma = Marshmallow(app)

class GroupSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('uuid', 'name', 'created_date')

class GroupMembershipSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('member_id', 'label', 'group_id', 'created_date')
