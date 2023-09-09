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
