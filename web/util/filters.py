from django_filters import FilterSet

from web.models.result import CORSRequestResult


class CORSRequestResultFilter(FilterSet):
    """Filter set for the CORSRequestResult model."""

    class Meta:
        model = CORSRequestResult
        fields = {
            "host_domain": ["contains"],
            "url": ["contains"],
            "url_domain": ["contains"],
            "err_msg": ["contains"],
            "err_location": ["contains"],
            "user_agent": ["contains"],
            "user_ip": ["contains"],
            "success": ["exact"],
        }
