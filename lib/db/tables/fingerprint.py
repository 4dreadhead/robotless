from datetime import datetime
from peewee import IntegerField, CharField, PrimaryKeyField, DateTimeField
from lib.db import Base
from lib.models import EnumExtended


class Fingerprint(Base):
    class Kind(EnumExtended):
        JA3 = 1
        AKAMAI = 2
        FINGERPRINTJS = 3
        CANVAS = 4
        WEBGL = 5

    id = PrimaryKeyField()
    hash = CharField(unique=True, max_length=64)
    value = CharField(max_length=512)
    kind = IntegerField(choices=Kind.values())
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    @property
    def kind_attr(self):
        return self.Kind.find(self.kind)
