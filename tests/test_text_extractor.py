from app.services.text_extractor import TextExtractor


def test_extract_text_from_plain_text():
    extractor = TextExtractor()
    content = "Mahal Kodu: ABC123".encode("utf-8")
    assert extractor.extract_text(content, filename="sample.txt") == "Mahal Kodu: ABC123"
