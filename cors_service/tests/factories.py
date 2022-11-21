from datetime import timedelta
from random import getrandbits
from typing import Generic, TypeVar
from uuid import UUID, uuid4

import factory.fuzzy
from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory

from web.models.scan import ScanDomain, ScanSummary
from web.models.target import TargetDomain, TargetSubdomain

T = TypeVar("T")
# TODO have children pull parent domains from references


def _flip_coin(*args) -> bool:
    return bool(getrandbits(1))


def _create_guid(*args) -> UUID:
    return uuid4()


def _get_domain_name(*args) -> str:
    return f"{uuid4()}.com"


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
    domain = factory.Sequence(_get_domain_name)
    scan_guid = factory.SelfAttribute("target_domain.last_scan_guid")

    class Meta:
        model = TargetSubdomain
