from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, status

from application.interactors.payment import CreatePaymentInteractor, GetPaymentInteractor
from application.dto.payment import CreatePaymentDTO
from infra.resources.database.repos import UOW
from infra.di.ioc import Container
from presentation.http.v1.mappers.payments import PaymentApiMapper
from presentation.http.v1.schemas.payments import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentDetailResponse,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create payment",
)
@inject
async def create_payment(
    body: CreatePaymentRequest,
    idempotency_key: UUID = Header(..., alias="Idempotency-Key"),
    interactor: CreatePaymentInteractor = Depends(Provide[Container.interactors.create]),
    mapper: PaymentApiMapper = Depends(Provide[Container.mappers.payment_mapper]),
    uow: UOW = Depends(Provide[Container.db.uow]),
) -> CreatePaymentResponse:
    dto = CreatePaymentDTO(
        amount=body.amount,
        currency=body.currency,
        description=body.description,
        metadata=body.metadata,
        webhook_url=str(body.webhook_url),
        idempotency_key=idempotency_key,
    )
    async with uow:
        entity = await interactor(dto=dto, uow=uow)
    return mapper.to_create_response(entity)


@router.get(
    "/{payment_id}",
    summary="Get payment by ID",
)
@inject
async def get_payment(
    payment_id: UUID,
    interactor: GetPaymentInteractor = Depends(Provide[Container.interactors.get]),
    mapper: PaymentApiMapper = Depends(Provide[Container.mappers.payment_mapper]),
    uow: UOW = Depends(Provide[Container.db.uow]),
) -> PaymentDetailResponse:
    async with uow:
        entity = await interactor(payment_id=payment_id, uow=uow)
    return mapper.to_detail_response(entity)
