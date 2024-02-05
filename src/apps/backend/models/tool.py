from enum import Enum
from django.db import models


class Tool(models.Model):
    class Kind(Enum):
        HTTP_CLIENT = 1
        BROWSER     = 2
        SEARCH_BOT  = 3
        MALWARE     = 4

    name         = models.CharField(max_length=64)
    version      = models.CharField(max_length=32, null=True)
    system       = models.CharField(max_length=64)
    kind         = models.IntegerField(choices=[(attr.value, attr.name) for attr in Kind])
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tool #{self.id} ({self.name} {self.version} on {self.system})"
