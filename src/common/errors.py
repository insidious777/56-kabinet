from rest_framework import status
from rest_framework.exceptions import APIException as OriginAPIException


class APIException(OriginAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
