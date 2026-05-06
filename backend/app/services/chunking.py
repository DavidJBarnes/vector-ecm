from dataclasses import dataclass
from functools import lru_cache

from app.config import get_settings


@dataclass
class Chunk:
    index: int
    text: str
    token_count: int = 0


class ChunkingService:
    """Splits documents into overlapping chunks for embedding."""

    def __init__(self):
        settings = get_settings()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str) -> list[Chunk]:
        if not text.strip():
            return []

        segments = self._split_recursive(text)
        chunks = [
            Chunk(index=i, text=seg, token_count=self._estimate_tokens(seg))
            for i, seg in enumerate(segments)
        ]
        return chunks

    def _split_recursive(self, text: str) -> list[str]:
        splits = [text]

        for separator in self.separators:
            new_splits: list[str] = []
            for s in splits:
                if len(s) <= self.chunk_size:
                    new_splits.append(s)
                elif separator:
                    parts = s.split(separator)
                    new_splits.extend(p for p in parts if p)
                else:
                    new_splits.append(s)
            splits = new_splits

        return self._merge_splits(splits)

    def _merge_splits(self, splits: list[str]) -> list[str]:
        if not splits:
            return []

        merged: list[str] = []
        current = ""

        for split in splits:
            if not current:
                current = split
                continue

            candidate = current + " " + split
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                merged.append(current.strip())
                if len(split) > self.chunk_size:
                    # Oversized chunk: take overlap from end of previous
                    overlap = current[-self.chunk_overlap :] if current else ""
                    current = overlap + " " + split
                else:
                    current = split

        if current.strip():
            merged.append(current.strip())

        return merged

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split())


@lru_cache
def get_chunking_service() -> ChunkingService:
    return ChunkingService()
