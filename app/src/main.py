from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from lifespan import lifespan
from presentation.http.authentication import auth_api_key_dep
from presentation.http.error_handlers import setup_exception_handlers
from routers import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Payment Service",
        description="Async payment processing service",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        dependencies=[auth_api_key_dep],
    )
    app.include_router(api_router)
    setup_exception_handlers(app)
    return app


main_app = create_app()

if __name__ == "__main__":
    import uvicorn

    # Set reload = False in production (use config)
    uvicorn.run("main:main_app", host="0.0.0.0", reload=True)
