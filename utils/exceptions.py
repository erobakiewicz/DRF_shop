from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from rest_framework.exceptions import ValidationError as APIValidationError

from utils.constants import ErrorMessages


class GlobalProductLimitObjectDoesNotExist(ObjectDoesNotExist):
    status_code = 400
    code = status.HTTP_400_BAD_REQUEST
    message = ErrorMessages.GLOBAL_LIMIT_NOT_SET


class GlobalLimitExceedException(ValidationError):
    status_code = 400
    message = ErrorMessages.GLOBAL_LIMIT_EXCEEDED


class RegionLimitExceedException(ValidationError):
    status_code = 400


class ObjectDoesNotExistAPIException(APIValidationError):
    status_code = 404
