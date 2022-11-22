from django.db import models

from web.models.base import BaseModel


class TargetDomain(BaseModel):
    """Database model for representing a single domain that is being targeted using CORS Hunter."""

    domain = models.TextField(
        null=False,
        blank=False,
        help_text="The parent domain that was used to start the scan.",
        db_index=True,
        unique=True,
    )
    last_scan_guid = models.UUIDField(
        null=False,
        blank=False,
        help_text="A UUID for identifying the most recent subdomains identified for this target.",
        db_index=True,
    )
    time_last_scan_set = models.DateTimeField(
        null=False,
        blank=False,
        help_text="The most recent time at which 'last_scan_guid' was set.",
    )


class HostDomain(BaseModel):
    """Database model for representing a domain that is served up as a host from the Django
    web server.
    """

    domain = models.TextField(
        null=False,
        blank=False,
        help_text="The domain we expect to receive HTTP requests to.",
        db_index=True,
        unique=True,
    )
    redirect_domain = models.TextField(
        null=False,
        blank=False,
        help_text="The domain that should be redirected to when a request is received to this host domain.",
    )
    targets = models.ManyToManyField(
        TargetDomain, related_name="hosts", through="HostToTargetMapping"
    )


class HostToTargetMapping(BaseModel):
    """Through table for maintaining a mapping from a domain that we are serving requests for to
    a target domain (or domains) that we serve payloads up for.
    """

    host_domain = models.ForeignKey(
        HostDomain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The host domain side of the mapping.",
    )
    target_domain = models.ForeignKey(
        TargetDomain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The target domain side of the mapping.",
    )
    active = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        help_text="Whether or not this mapping should be considered active.",
    )

    class Meta:
        unique_together = ("host_domain", "target_domain")


class TargetSubdomain(BaseModel):
    """Database model for representing a single subdomain that is being targeted using CORS Hunter."""

    target_domain = models.ForeignKey(
        TargetDomain,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The parent domain that this subdomain is being targeted under.",
    )
    domain = models.TextField(
        null=False,
        blank=False,
        help_text="The subdomain to use in payload generation for the parent target.",
        db_index=True,
    )
    scan_guid = models.UUIDField(
        null=False,
        blank=False,
        help_text="The scan batch GUID from the target domain wherein this subdomain was added.",
    )

    class Meta:
        unique_together = ("domain", "scan_guid")
