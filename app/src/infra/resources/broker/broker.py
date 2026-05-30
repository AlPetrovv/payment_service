from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

from domain.enums import OutboxEventType
from infra.core.config import settings

broker = RabbitBroker(str(settings.rabbitmq.url))

# --- Exchanges -------------------------------------------------------------
# May be Topic instead of Direct
# payments - > new, retry, dead

payments_exchange = RabbitExchange("payments", type=ExchangeType.DIRECT, durable=True)
# webhooks - > send, retry, dead
webhooks_exchange = RabbitExchange("webhooks", type=ExchangeType.DIRECT, durable=True)
# retry - > payments, webhooks
retry_exchange = RabbitExchange("retry", type=ExchangeType.DIRECT, durable=True)


# --- Outbox routing --------------------------------------------------------
EVENT_ROUTES: dict[OutboxEventType, tuple[RabbitExchange, str]] = {
    OutboxEventType.PAYMENT_CREATED: (payments_exchange, "new"),
    OutboxEventType.PAYMENT_PROCESSED: (webhooks_exchange, "send"),
}


# --- Payment queues --------------------------------------------------------
payments_queue = RabbitQueue(
    "payments.new",
    durable=True,
    routing_key="new",
    arguments={  # noqa
        "x-dead-letter-exchange": "retry",  # send to retry exchange
        "x-dead-letter-routing-key": "payments.dead",
    },
)

#
payments_retry_queue = RabbitQueue(
    "payments.retry",
    durable=True,
    routing_key="payments.retry",
    arguments={  # noqa
        "x-dead-letter-exchange": "payments",
        "x-dead-letter-routing-key": "new",
    },
)

# Dead (after retries)
payments_dlq = RabbitQueue("payments.dead", durable=True, routing_key="payments.dead")


# --- Webhook queues --------------------------------------------------------
webhooks_queue = RabbitQueue(
    "webhooks.send",
    durable=True,
    routing_key="send",
    arguments={  # noqa
        "x-dead-letter-exchange": "retry",
        "x-dead-letter-routing-key": "webhooks.dead",
    },
)

webhooks_retry_queue = RabbitQueue(
    "webhooks.retry",
    durable=True,
    routing_key="webhooks.retry",
    arguments={  # noqa
        "x-dead-letter-exchange": "webhooks",
        "x-dead-letter-routing-key": "send",
    },
)

webhooks_dlq = RabbitQueue("webhooks.dead", durable=True, routing_key="webhooks.dead")


_BINDINGS = (
    (payments_queue, payments_exchange, "new"),
    (payments_retry_queue, retry_exchange, "payments.retry"),
    (payments_dlq, retry_exchange, "payments.dead"),
    (webhooks_queue, webhooks_exchange, "send"),
    (webhooks_retry_queue, retry_exchange, "webhooks.retry"),
    (webhooks_dlq, retry_exchange, "webhooks.dead"),
)


async def setup_broker(broker_: RabbitBroker) -> None:
    """Declare every exchange/queue and bind them."""
    declared_exchanges = {}
    for exchange in (payments_exchange, webhooks_exchange, retry_exchange):
        declared_exchanges[exchange.name] = await broker_.declare_exchange(exchange)

    for queue, exchange, routing_key in _BINDINGS:
        declared_queue = await broker_.declare_queue(queue)
        await declared_queue.bind(declared_exchanges[exchange.name], routing_key=routing_key)
