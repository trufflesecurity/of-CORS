from datetime import timedelta
from random import getrandbits
from typing import Generic, TypeVar
from uuid import UUID, uuid4

import factory.fuzzy
from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory

from web.models.scan import ScanDomain, ScanSummary
from web.models.target import (
    HostDomain,
    HostToTargetMapping,
    TargetDomain,
    TargetSubdomain,
)

T = TypeVar("T")
# TODO have children pull parent domains from references


def _flip_coin(*args) -> bool:
    return bool(getrandbits(1))


def _create_guid(*args) -> UUID:
    return uuid4()


def _get_domain_name(*args) -> str:
    return f"{uuid4()}.com"


def get_populated_host_domain(
    targets_count: int = 3, subdomains_count: int = 10
) -> HostDomain:
    """Create and return a populated host domain that has the configured amount of enabled targets
    and the configured amount of subdomains for each of those targets.
    """
    target_domains = []
    target_subdomains = []
    for i in range(targets_count):
        new_target_domain = TargetDomainFactory()
        target_domains.append(new_target_domain)
        for j in range(subdomains_count):
            target_subdomains.append(
                TargetSubdomainFactory(target_domain=new_target_domain)
            )
    host_domain = HostDomainFactory()
    for target_domain in target_domains:
        HostToTargetMappingFactory(
            host_domain=host_domain,
            target_domain=target_domain,
            active=True,
        )
    return host_domain


class BaseFactory(Generic[T], DjangoModelFactory):
    """This is a base factory class for enabling MyPy typing for Django model factories."""

    def __new__(cls, *args, **kwargs) -> T:  # type: ignore
        return super().__new__(*args, **kwargs)


class ScanSummaryFactory(BaseFactory):
    """Factory class for generating new ScanSummary objects."""

    parent_domain = factory.Sequence(_get_domain_name)
    subdomains_count = factory.fuzzy.FuzzyInteger(low=0)
    https_subdomains_count = factory.fuzzy.FuzzyInteger(low=0)
    time_started = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now(), end_dt=timezone.now() + timedelta(seconds=60)
    )
    time_completed = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(seconds=60),
        end_dt=timezone.now() + timedelta(seconds=120),
    )

    class Meta:
        model = ScanSummary


class ScanDomainFactory(BaseFactory):
    """Factory class for generating new ScanDomain objects."""

    summary = SubFactory("tests.factories.ScanSummaryFactory")
    domain = factory.Sequence(_get_domain_name)
    has_https = factory.Sequence(_flip_coin)

    class Meta:
        model = ScanDomain


class TargetDomainFactory(BaseFactory):
    """Factory class for generating new TargetDomain objects."""

    domain = factory.Sequence(_get_domain_name)
    last_scan_guid = factory.Sequence(_create_guid)
    time_last_scan_set = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now(), end_dt=timezone.now() + timedelta(seconds=60)
    )

    class Meta:
        model = TargetDomain


class TargetSubdomainFactory(BaseFactory):
    """Factory class for generating new TargetSubdomain objects."""

    target_domain = SubFactory("tests.factories.TargetDomainFactory")
    # TODO populate this from domain of TargetDomain parent
    domain = factory.Sequence(_get_domain_name)
    scan_guid = factory.SelfAttribute("target_domain.last_scan_guid")

    class Meta:
        model = TargetSubdomain


class HostDomainFactory(BaseFactory):
    """Factory class for generating new HostDomain objects."""

    domain = factory.Sequence(_get_domain_name)
    redirect_domain = factory.Sequence(_get_domain_name)

    class Meta:
        model = HostDomain


class HostToTargetMappingFactory(BaseFactory):
    """Factory class for generating new records for the HostToTargetMapping through table."""

    host_domain = SubFactory("tests.factories.HostDomainFactory")
    target_domain = SubFactory("tests.factories.TargetDomainFactory")
    active = factory.Sequence(_flip_coin)

    class Meta:
        model = HostToTargetMapping
