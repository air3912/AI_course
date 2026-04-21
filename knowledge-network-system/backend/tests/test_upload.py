from app.utils.file_types import is_supported_upload


def test_supported_upload_types() -> None:
    assert is_supported_upload("a.pdf")
    assert is_supported_upload("a.ppt")
    assert is_supported_upload("a.pptx")
    assert not is_supported_upload("a.docx")
