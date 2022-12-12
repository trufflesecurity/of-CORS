from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from web.logic.results import ResultManager
from web.util.request import get_client_ip, get_client_user_agent, get_request_host
from web.util.string import can_base64_decode


class CORSSuccessRequestSerializer(serializers.Serializer):
    """Request data serializer for the cors_success endpoint."""

    url = serializers.URLField(required=True, allow_null=False, allow_blank=False)
    content = serializers.CharField(required=True, allow_blank=True, allow_null=False)
    status = serializers.IntegerField(required=True, allow_null=False)
    duration = serializers.FloatField(required=True, allow_null=False)


@api_view(["POST"])
def cors_success(request: Request) -> Response:
    """API handler for receiving the results of a successful CORS request from our service worker payload."""
    serializer = CORSSuccessRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if not can_base64_decode(serializer.validated_data["content"]):
        raise serializers.ValidationError("Content cannot be base64 decoded.")
    ResultManager.accept_success(
        host=get_request_host(request=request),
        fetched_url=serializer.validated_data["url"],
        content=serializer.validated_data["content"],
        duration=serializer.validated_data["duration"],
        status_code=serializer.validated_data["status"],
        user_agent=get_client_user_agent(request=request),
        user_ip=get_client_ip(request=request),
    )
    return Response(status=201)


class CORSFailureRequestSerializer(serializers.Serializer):
    """Request data serializer for the cors_failure endpoint."""

    url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    location = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    err_msg = serializers.CharField(required=True, allow_blank=True, allow_null=False)
    duration = serializers.FloatField(required=True, allow_null=False)


@api_view(["POST"])
def cors_failure(request: Request) -> Response:
    """API handler for receiving the results of a failedCORS request from our service worker payload."""
    serializer = CORSFailureRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ResultManager.accept_failure(
        host=get_request_host(request=request),
        fetched_url=serializer.validated_data.get("url"),
        err_msg=serializer.validated_data["err_msg"],
        err_location=serializer.validated_data["location"],
        duration=serializer.validated_data["duration"],
        user_agent=get_client_user_agent(request=request),
        user_ip=get_client_ip(request=request),
    )
    return Response(status=201)
