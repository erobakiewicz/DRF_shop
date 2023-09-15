from django.db import models


class ErrorMessages:
    GLOBAL_LIMIT_NOT_SET = "Global limit not set."
    GLOBAL_LIMIT_EXCEEDED = "Global limit exceeded."

    REGION_DOES_NOT_EXIST = "Region does not exist."
    REGION_ACCESS_ERROR = "Region cannot have closed and unlimited access at the same time."
    REGION_LIMIT_EXCEEDED = "Region {}: closed or limit exceeded."

    CART_USER_MISMATCH = "Cart does not belong to user or does not exist."


class CartStatuses(models.IntegerChoices):
    OPEN = 10
    CLOSED = 20


class OrderStatuses(models.IntegerChoices):
    PENDING = 10
    COMPLETED = 20
    CANCELED = 30
