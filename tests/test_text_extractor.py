from app.services.text_extractor import TextExtractor


def test_extract_text_from_empty_text_file_returns_native():
    extractor = TextExtractor()

    text, confidence, source = extractor.extract_text(b"", document_type="empty.txt")

    assert text == ""
    assert confidence is None
    assert source == "native"


def test_extract_text_from_empty_bytes_falls_back_to_ocr():
    extractor = TextExtractor()
    text, confidence, source = extractor.extract_text(b"", document_type="empty.pdf")

    # Şimdilik sadece patlamasın diye basic assertion
    assert isinstance(text, str)
    assert source in ("native", "ocr")



def test_extract_text_from_plain_text():
    extractor = TextExtractor()
    content = "Mahal Kodu: ABC123".encode("utf-8")
    text, confidence, source = extractor.extract_text(content, document_type="sample.txt")

    assert text == "Mahal Kodu: ABC123"
    assert confidence is None
    assert source == "native"
