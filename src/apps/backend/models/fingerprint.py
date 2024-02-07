from django.db import models


class Fingerprint(models.Model):
    class Kind(models.IntegerChoices):
        JA3    = 0
        JA3N   = 1
        HTTP2  = 2
        JS     = 3
        CANVAS = 4
        WEBGL  = 5

    hash       = models.CharField(unique=True, max_length=64)
    value      = models.CharField(max_length=512)
    kind       = models.IntegerField(choices=Kind.choices)
    tools      = models.ManyToManyField('Tool', related_name='fingerprints')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fingerprint #{self.id} ({self.Kind(self.kind).name})"
