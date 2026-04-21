from app.db.session import engine
from app.models.base import Base
from app.models.document import Document  # noqa: F401
from app.models.graph import GraphSnapshot  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")


if __name__ == "__main__":
    main()
