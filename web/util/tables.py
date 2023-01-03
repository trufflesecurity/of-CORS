from typing import Any, Optional, Type

from django.http import QueryDict
from django.urls import reverse
from django.utils.html import format_html
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2 import Column, SingleTableMixin, tables  # type: ignore[import]

from web.models.result import CORSRequestResult


class FilteredSingleTableView(SingleTableMixin, FilterView):
    """Base class for presenting a single table that comes with the ability to filter the
    referenced QuerySet.

    https://gist.github.com/ckrybus/1c597830ed6d0dead642fd4cb31f3b7e
    """

    filter_defaults: dict[str, Any]

    def get_filterset_kwargs(self, filterset_class: Type[FilterSet]) -> dict[str, Any]:
        """Custom implementation of get_filterset_kwargs to include defaults configuration.

        https://stackoverflow.com/questions/48507955/django-filterset-set-initial-value
        """
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"] is None:
            filter_values = QueryDict(mutable=True)
        else:
            filter_values = kwargs["data"].copy()
        for k, v in self.filter_defaults.items():
            if k not in filter_values:
                filter_values[k] = v
        kwargs["data"] = filter_values
        return kwargs

    def get_filterset(self, filterset_class: Type[FilterSet]) -> FilterSet:
        kwargs = self.get_filterset_kwargs(filterset_class)
        filterset = filterset_class(**kwargs)
        return filterset


class CORSRequestResultTable(tables.Table):
    """Table definition for visualizing CORSRequestResult objects."""

    html_content = Column(empty_values=())

    def render_html_content(self, record: CORSRequestResult) -> Optional[str]:
        if not record.success:
            return "—"
        if not record.content:
            return "—"
        url = reverse(viewname="view_result_html", kwargs={"result_id": record.id})
        return format_html(f'<a target="_blank" href="{url}">View HTML Content</a>')

    class Meta:
        model = CORSRequestResult
        template_name = "django_tables2/bootstrap.html"
        exclude = ("guid", "time_updated", "content", "duration", "url_domain")
