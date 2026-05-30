from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from application.interactors.payment import CreatePaymentInteractor, GetPaymentInteractor
from infra.core.config import settings
from infra.resources.database.manager import DatabaseSessionManager
from infra.resources.database.repos import UOW
from presentation.amqp.services.gateway import PaymentGateway
from presentation.amqp.services.webhook import WebhookSender
from presentation.http.v1.mappers.payments import PaymentApiMapper


class DatabaseContainer(DeclarativeContainer):
    config = providers.Configuration()

    engine_kwargs = providers.Dict(
        echo=config.db.echo,
        echo_pool=config.db.echo_pool,
        pool_size=config.db.pool_size,
        max_overflow=config.db.max_overflow,
        pool_pre_ping=config.db.pool_pre_ping,
    )

    db_manager = providers.Singleton(
        DatabaseSessionManager,
        db_url=config.db.url,
        engine_kwargs=engine_kwargs,
    )
    uow = providers.Factory(UOW, db_manager=db_manager)


class InteractorsContainer(DeclarativeContainer):
    create = providers.Factory(CreatePaymentInteractor)
    get = providers.Factory(GetPaymentInteractor)


class MappersContainer(DeclarativeContainer):
    payment_mapper = providers.Factory(PaymentApiMapper)


class ServicesContainer(DeclarativeContainer):
    config = providers.Configuration()

    gateway = providers.Singleton(PaymentGateway)
    webhook_sender = providers.Singleton(WebhookSender, timeout=config.webhook_timeout)


class Container(DeclarativeContainer):
    config = providers.Configuration()

    db: DatabaseContainer = providers.Container(DatabaseContainer, config=config)
    interactors: InteractorsContainer = providers.Container(InteractorsContainer)
    mappers: MappersContainer = providers.Container(MappersContainer)
    services: ServicesContainer = providers.Container(ServicesContainer, config=config)


def build_container() -> Container:
    """Build the DI container"""
    container = Container()
    container.config.from_pydantic(settings)
    return container
