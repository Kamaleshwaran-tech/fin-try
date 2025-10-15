from app import create_app
from app.core.config import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    app.run(host=settings.host, port=settings.port)
