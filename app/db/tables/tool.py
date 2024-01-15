from datetime import datetime
from peewee import CharField, PrimaryKeyField, IntegerField, ManyToManyField, DateTimeField
from app.customs import EnumExtended
from app.db import Base
from app.db.tables import Fingerprint


class Tool(Base):
    class Kind(EnumExtended):
        HTTP_CLIENT = 1
        BROWSER = 2
        SEARCH_BOT = 3
        MALWARE = 4

    id = PrimaryKeyField()
    name = CharField(max_length=64)
    version = CharField(max_length=32, null=True)
    system = CharField(max_length=64)
    kind = IntegerField(choices=Kind.values())
    fingerprints = ManyToManyField(Fingerprint, backref='tools')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    @property
    def kind_attr(self):
        return self.Kind.find(self.kind)

    @property
    def as_str(self):
        result = self.name
        if self.version:
            result += "\t" + self.version + "\t"
        result += self.system
        return result
