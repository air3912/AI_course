from app.services.file_service import FileService
from app.services.graph_service import GraphService


def get_file_service() -> FileService:
    return FileService()


def get_graph_service() -> GraphService:
    return GraphService()
