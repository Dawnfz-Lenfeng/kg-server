from enum import Enum

from pydantic import BaseModel, Field, model_validator


class OCREngine(str, Enum):
    CNOCR = "cnocr"
    TESSERACT = "tesseract"
    # PADDLEOCR = "paddleocr"


class ExtractConfig(BaseModel):
    num_workers: int = Field(
        default=4, description="Number of parallel workers for text extraction"
    )
    first_page: int = Field(
        default=1, ge=1, description="First page to extract (1-based)"
    )
    last_page: int | None = Field(
        default=None,
        examples=[None],
        description="Last page to extract (None for all pages)",
    )
    ocr_engine: OCREngine = Field(
        default=OCREngine.CNOCR,
        description="OCR engine to use for image-based documents",
    )
    force_ocr: bool = Field(
        default=False, description="Force OCR even for PDF documents with embedded text"
    )

    @model_validator(mode="after")
    def validate_pages(self) -> "ExtractConfig":
        if self.last_page is not None and self.last_page < self.first_page:
            raise ValueError("last_page must be greater than or equal to first_page")
        return self


class NormalizeConfig(BaseModel):
    char_threshold: int = Field(
        default=2, description="Minimum length of characters to keep"
    )
    sentence_threshold: float = Field(
        default=0.9, description="Similarity threshold for merging similar sentences"
    )
