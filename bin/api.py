import uvicorn

from app.settings import Settings


def main() -> None:
    settings = Settings()

    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


if __name__ == '__main__':
    main()
