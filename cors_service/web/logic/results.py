from typing import Any
from urllib.parse import urlparse

from web.models.result import CORSRequestResult


class ResultManager:
    """Manager class for containing all methods related to the receipt and processing of CORS
    scanning results.
    """

    @staticmethod
    def accept_success(
        host: str,
        fetched_url: str,
        content: str,
        duration: float,
        request_meta: dict[str, Any],
    ) -> CORSRequestResult:
        """Record that a successful CORS request was observed for the given URL. Return the associated
        database record once created.
        """
        parsed = urlparse(fetched_url)
        result = CORSRequestResult(
            host_domain=host,
            url=fetched_url,
            url_domain=parsed.netloc,
            content=content,
            duration=duration,
            success=True,
            client_meta=request_meta,
        )
        result.save()
        return result

    @staticmethod
    def accept_failure(
        host: str,
        fetched_url: str,
        err_msg: str,
        duration: float,
        request_meta: dict[str, Any],
    ) -> CORSRequestResult:
        """Record that a CORS request failed for the given URL and reason. Return the associated
        database record once created.
        """
        parsed = urlparse(fetched_url)
        result = CORSRequestResult(
            host_domain=host,
            url=fetched_url,
            url_domain=parsed.netloc,
            err_msg=err_msg,
            duration=duration,
            success=True,
            client_meta=request_meta,
        )
        result.save()
        return result
