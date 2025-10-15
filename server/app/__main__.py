from . import create_app
from .core.config import get_settings

app = create_app()

if __name__ == "__main__":  # pragma: no cover
    settings = get_settings()
    app.run(host=settings.host, port=settings.port)
