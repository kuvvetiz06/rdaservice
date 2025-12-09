# RDA Service

Yerel OCR + LLM tabanlı sözleşme analiz servisi. FastAPI ile sunulan API,
PDF veya görüntü dosyalarından metin çıkarır, regex ve LLM ile alanları
doldurur ve birleşik bir JSON döner.

## Çalıştırma

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```
