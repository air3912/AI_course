SUPPORTED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}


def is_supported_upload(filename: str | None) -> bool:
    if not filename or "." not in filename:
        return False
    ext = "." + filename.lower().rsplit(".", 1)[-1]
    return ext in SUPPORTED_EXTENSIONS


def detect_file_type(filename: str) -> str:
    ext = "." + filename.lower().rsplit(".", 1)[-1]
    return ext.lstrip(".")
