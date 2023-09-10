class ErrorMessages:
    GLOBAL_LIMIT_NOT_SET = "Global limit not set."
    GLOBAL_LIMIT_EXCEEDED = "Global limit exceeded."

    SHELF_DOES_NOT_EXIST = "Shelf does not exist."
    REGION_DOES_NOT_EXIST = "Region does not exist."
    REGION_ACCESS_ERROR = "Region cannot have closed and unlimited access at the same time."
    REGION_LIMIT_EXCEEDED = "Region {}: closed or limit exceeded."

    CART_USER_MISMATCH = "Cart does not belong to user or does not exist."

    ORDER_CART_REGIONS_MISMATCH = "Cart and order regions don't match."


class CartStatuses:
    OPEN = 10
    CLOSED = 20

    Choices = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
    )


class OrderStatuses:
    PENDING = 10
    COMPLETED = 20
    CANCELED = 30

    Choices = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    )
