from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import UnicodeText
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy.orm import relationship


from speak_friend.events import ACTIVITIES
from speak_friend.models import Base
from speak_friend.models.controlpanel import JSON
from speak_friend.models.profiles import UserProfile


class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = (
        {'schema': 'reports'}
    )
    activity = Column(
        UnicodeText,
        primary_key=True,
    )

    def __init__(self, activity):
        self.activity = activity

    def __repr__(self):
        return u"<Activity(%s)>" % self.activity

def after_activity_create(target, connection, **kw):
    for aname in ACTIVITIES:
        connection.execute(target.insert(), activity=aname)

event.listen(Activity.__table__, "after_create", after_activity_create)


class UserActivity(Base):
    __tablename__ = 'user_activity'
    __table_args__ = (
        {'schema': 'reports'}
    )
    user_activity_id = Column(
        Integer,
        primary_key=True
    )
    username = Column(
        UnicodeText,
        ForeignKey("profiles.user_profiles.username"),
        nullable=False,
        index=True,
    )
    user = relationship(
        "UserProfile",
        foreign_keys=[UserProfile.username],
        primaryjoin="UserActivity.username==UserProfile.username",
    )
    activity = Column(
        UnicodeText,
        ForeignKey("reports.activities.activity"),
        nullable=False,
        index=True
    )
    activity_ts = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        index=True,
    )
    actor_username = Column(
        UnicodeText,
        ForeignKey("profiles.user_profiles.username")
    )
    actor = relationship(
        "UserProfile",
        foreign_keys=[UserProfile.username],
        primaryjoin="UserActivity.username==UserProfile.username",
    )
    activity_detail = Column(
        JSON,
    )

    def __init__(self, **attrs):
        if 'username' not in attrs and \
           'user' not in attrs:
            raise KeyError('Missing key: user')
        elif 'user' in attrs and \
           'username' not in attrs:
            attrs['username'] = attrs['user'].username
        if 'actor' in attrs and \
           attrs['actor'] and \
           'actor_username' not in attrs:
            attrs['actor_username'] = attrs['actor'].username
        if 'activity' not in attrs:
            raise KeyError('Missing key: activity')

        for attr, value in attrs.items():
            if attr in self.__table__.columns:
                setattr(self, attr, value)


    def __repr__(self):
        return u"<UserActivity(%s, %s)>" % (self.username, self.activity)