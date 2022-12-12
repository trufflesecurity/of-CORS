from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    """This is a base model class for handling a standard set of operations and fields that
    we want in all of our database models.
    """

    id = models.AutoField(primary_key=True)
    guid = models.UUIDField(
        default=uuid4,
        editable=False,
        db_index=True,
        help_text="A more or less 'secondary' primary key to reference this DB object.",
    )
    time_created = models.DateTimeField(
        auto_now_add=True,
        help_text="The time at which this record was created.",
    )
    time_updated = models.DateTimeField(
        auto_now=True,
        help_text="The time at which this record was last updated.",
    )

    class Meta:
        abstract = True
