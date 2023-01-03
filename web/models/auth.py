from django.db import models

from web.models.base import BaseModel


class AuthTicket(BaseModel):
    """Database model for representing a single ticket that can be used from the command line
    to authenticate to the results viewing pages.
    """

    used = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        help_text="Whether or not this ticket has been used yet.",
    )
    used_at = models.DateTimeField(
        null=True, blank=True, help_text="The time at which this ticket was used."
    )
