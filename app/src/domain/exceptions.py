class DomainError(Exception):
    """Base domain error carrying the HTTP status and message it maps to."""

    status_code: int = 500
    detail: str = "Internal error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class PaymentNotFoundError(DomainError):
    status_code = 404
    detail = "Payment not found"


class DuplicateIdempotencyKeyError(DomainError):
    status_code = 409
    detail = "Idempotency key conflict"


class InvalidPaymentStateError(DomainError):
    status_code = 409
    detail = "Invalid payment state"


class UnsupportedCurrencyError(DomainError):
    status_code = 422
    detail = "Unsupported currency"
