from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(["GET"])
def index(request: Request) -> Response:
    return Response({"hello": "world"})
