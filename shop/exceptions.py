from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.exceptions import ValidationError as APIValidationError


class ShelfObjectDoesNotExistException(ObjectDoesNotExist):
    status_code = 404
    default_code = '404'


class RegionObjectDoesNotExistException(ObjectDoesNotExist):
    status_code = 404
    default_code = '404'


class CartObjectDoesNotExistException(ObjectDoesNotExist):
    status_code = 404
    default_code = '404'


class GlobalProductLimitObjectDoesNotExist(ObjectDoesNotExist):
    status_code = 400


class GlobalLimitExceedException(ValidationError):
    status_code = 400


class RegionLimitExceedException(ValidationError):
    status_code = 400


class ObjectDoesNotExistAPIException(APIValidationError):
    status_code = 404
