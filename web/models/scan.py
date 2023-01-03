from django.db import models

from web.models.base import BaseModel


class ScanSummary(BaseModel):
    """Database model for containing the results of a scan targeting a single parent domain."""

    parent_domain = models.TextField(
        null=False,
        blank=False,
        help_text="The parent domain that was used to start the scan.",
        db_index=True,
    )
    subdomains_count = models.IntegerField(
        null=False,
        blank=False,
        help_text="The number of subdomains that were discovered.",
    )
    https_subdomains_count = models.IntegerField(
        null=False,
        blank=False,
        help_text="The number of subdomains that were discovered to have HTTPS available / enabled.",
    )
    time_started = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The time at which the scan started.",
    )
    time_completed = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The time at which the scan ended.",
    )


class ScanDomain(BaseModel):
    """Database model for representing a single domain that was discovered during a parent
    domain scan.
    """

    summary = models.ForeignKey(
        ScanSummary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The scan where this domain was identified.",
    )
    domain = models.TextField(
        null=False,
        blank=False,
        help_text="The domain that was discovered.",
        db_index=True,
    )
    has_https = models.BooleanField(
        null=False,
        blank=False,
        help_text="Whether or not this domain had an HTTP services available / enabled.",
    )
