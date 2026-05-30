from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader

from infra.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return api_key


auth_api_key_dep = Depends(get_api_key)
