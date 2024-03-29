from base64 import b64decode
from typing import Optional

from django.db import models

from web.models.base import BaseModel


class CORSRequestResult(BaseModel):
    """Database model for containing the results of an attempted CORS fetch from a client that visited
    one of the configured host domains.
    """

    host_domain = models.TextField(
        null=False,
        blank=False,
        help_text="The host domain that the CORS request result originated from.",
        db_index=True,
    )
    url = models.URLField(
        null=True,
        blank=True,
        help_text="The URL that was requested.",
    )
    url_domain = models.TextField(
        null=False,
        blank=False,
        help_text="The domain of the URL that was requested.",
        db_index=True,
    )
    duration = models.FloatField(
        null=False,
        blank=False,
        help_text="The amount of time elapsed between request start and either response or error.",
    )
    success = models.BooleanField(
        null=False,
        blank=False,
        help_text="Whether or not the request was successful.",
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Base64-encoded HTML content that was retrieved from the URL.",
    )
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="The HTTP status code returned from requesting the associated URL.",
    )
    err_msg = models.TextField(
        null=True,
        blank=True,
        help_text="A string denoting the type of error that was observed when a fetch was attempted of the URL.",
    )
    err_location = models.TextField(
        null=True,
        blank=True,
        help_text="The location where the error was thrown (if an error was thrown).",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="The user agent provided by the submitting user.",
    )
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="The IP address provided by the submitting user.",
    )

    @property
    def decoded_content(self) -> Optional[str]:
        """Return the properly decoded HTML content of this record if the record has any content."""
        if not self.content:
            return None
        return b64decode(self.content.encode("utf-8")).decode("utf-8")

    class Meta:
        ordering = ["user_ip", "time_created"]
