from dataclasses import dataclass
from functools import lru_cache

import fitz  # pymupdf


@dataclass
class ExtractedFile:
    title: str
    content: str


class FileExtractionService:
    SUPPORTED_TEXT = {".txt", ".md", ".csv", ".json", ".html", ".xml", ".py", ".js", ".ts"}
    SUPPORTED_PDF = {".pdf"}

    def extract(self, filename: str, content: bytes) -> ExtractedFile:
        suffix = self._suffix(filename)

        if suffix in self.SUPPORTED_PDF:
            return self._extract_pdf(filename, content)
        elif suffix in self.SUPPORTED_TEXT:
            return self._extract_text(filename, content)
        else:
            return self._extract_text(filename, content)

    def _extract_text(self, filename: str, content: bytes) -> ExtractedFile:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("utf-8", errors="replace")

        text = text.replace("\x00", "")
        title = self._filename_without_ext(filename)
        return ExtractedFile(title=title, content=text)

    def _extract_pdf(self, filename: str, content: bytes) -> ExtractedFile:
        doc = fitz.open(stream=content, filetype="pdf")
        pages = []
        for page in doc:
            text = page.get_text()
            if text:
                pages.append(text)
        doc.close()

        full_text = "\n\n".join(pages).replace("\x00", "")
        title = self._filename_without_ext(filename)
        return ExtractedFile(title=title, content=full_text)

    def _suffix(self, filename: str) -> str:
        dot = filename.rfind(".")
        if dot == -1:
            return ""
        return filename[dot:].lower()

    def _filename_without_ext(self, filename: str) -> str:
        dot = filename.rfind(".")
        if dot == -1:
            return filename
        return filename[:dot]


@lru_cache
def get_file_extraction_service() -> FileExtractionService:
    return FileExtractionService()
