from app.services.text_extractor import TextExtractor


def test_extract_text_from_plain_text():
    extractor = TextExtractor()
    content = "Mahal Kodu: ABC123".encode("utf-8")
    text, confidence, source = extractor.extract_text(content, document_type="sample.txt")

    assert text == "Mahal Kodu: ABC123"
    assert confidence is None
    assert source == "native"
