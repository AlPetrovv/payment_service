import asyncio
import random
from uuid import UUID

from loguru import logger


class PaymentGateway:
    async def process(self, payment_id: UUID) -> bool:
        """Process payment via gateway"""
        delay = random.uniform(2, 5)
        await asyncio.sleep(delay)
        success = random.random() < 0.9
        logger.info("Gateway processed payment={} success={} delay={:.2f}s", payment_id, success, delay)
        return success
