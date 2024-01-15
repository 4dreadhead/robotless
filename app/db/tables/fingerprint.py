from datetime import datetime
from peewee import IntegerField, CharField, PrimaryKeyField, DateTimeField
from app.db import Base
from app.customs import EnumExtended


class Fingerprint(Base):
    class Kind(EnumExtended):
        JA3 = 1
        JA3N = 2
        AKAMAI = 3
        FINGERPRINTJS = 4
        CANVAS = 5
        WEBGL = 6

    id = PrimaryKeyField()
    hash = CharField(unique=True, max_length=64)
    value = CharField(max_length=512)
    kind = IntegerField(choices=Kind.values())
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    @property
    def kind_attr(self):
        return self.Kind.find(self.kind)
