"""Safe parsers for digitally readable PDF, DOCX, Markdown, and text."""

from __future__ import annotations

import hashlib
import io
import unicodedata
import zipfile
from collections.abc import Iterable, Sequence
from xml.etree import ElementTree

import pymupdf

from shaper.domain import SourceDocument, SourceSpan

_WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_WORD_PARAGRAPH = f"{{{_WORD_NAMESPACE}}}p"
_WORD_TEXT = f"{{{_WORD_NAMESPACE}}}t"
_WORD_TAB = f"{{{_WORD_NAMESPACE}}}tab"
_WORD_BREAKS = {
    f"{{{_WORD_NAMESPACE}}}br",
    f"{{{_WORD_NAMESPACE}}}cr",
}
_WORD_STYLE = f"{{{_WORD_NAMESPACE}}}pStyle"
_WORD_VALUE = f"{{{_WORD_NAMESPACE}}}val"


class DocumentParseError(ValueError):
    """Raised when a supported document cannot produce safe readable spans."""


class SupportedDocumentParser:
    """Parse supported formats into ordered immutable spans."""

    def __init__(self, *, maximum_spans: int = 10_000) -> None:
        self._maximum_spans = maximum_spans

    def parse(self, document: SourceDocument, content: bytes) -> Sequence[SourceSpan]:
        """Parse content based on its validated media type."""
        try:
            if document.media_type == "application/pdf":
                blocks = self._pdf_blocks(content)
            elif (
                document.media_type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                blocks = self._docx_blocks(content)
            elif document.media_type in {"text/markdown", "text/plain"}:
                blocks = self._text_blocks(
                    content,
                    markdown=document.media_type == "text/markdown",
                )
            else:
                raise DocumentParseError(
                    f"Source {document.source_id!r} has unsupported media type "
                    f"{document.media_type!r}; use PDF, DOCX, Markdown, or plain text"
                )
            return self._spans(document, blocks)
        except DocumentParseError:
            raise
        except (
            ElementTree.ParseError,
            OSError,
            RuntimeError,
            UnicodeError,
            ValueError,
            zipfile.BadZipFile,
        ) as error:
            raise DocumentParseError(
                f"Could not parse source {document.source_id!r} as {document.media_type!r}; "
                "verify that the file is digitally readable and not corrupt"
            ) from error

    def _spans(
        self,
        document: SourceDocument,
        blocks: Iterable[tuple[str, tuple[str, ...], dict[str, int | str]]],
    ) -> tuple[SourceSpan, ...]:
        spans: list[SourceSpan] = []
        for ordinal, (raw_text, headings, location) in enumerate(blocks):
            text = unicodedata.normalize("NFC", raw_text).strip()
            if not text:
                continue
            if len(spans) >= self._maximum_spans:
                raise DocumentParseError(
                    f"Source {document.source_id!r} exceeds the "
                    f"{self._maximum_spans}-span parser limit"
                )
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            span_key = (
                f"{document.source_id}:{document.source_version}:{ordinal}:{text_hash}".encode()
            )
            spans.append(
                SourceSpan(
                    span_id=hashlib.sha256(span_key).hexdigest()[:32],
                    source_id=document.source_id,
                    source_version=document.source_version,
                    ordinal=ordinal,
                    text=text,
                    text_hash=text_hash,
                    heading_path=headings,
                    location=location,
                )
            )
        return tuple(spans)

    @staticmethod
    def _text_blocks(
        content: bytes,
        *,
        markdown: bool,
    ) -> Iterable[tuple[str, tuple[str, ...], dict[str, int | str]]]:
        text = content.decode("utf-8")
        headings: list[str] = []
        paragraph: list[str] = []
        block = 0
        for line in [*text.splitlines(), ""]:
            stripped = line.strip()
            if markdown and stripped.startswith("#"):
                if paragraph:
                    yield "\n".join(paragraph), tuple(headings), {"block": block}
                    paragraph.clear()
                    block += 1
                level = len(stripped) - len(stripped.lstrip("#"))
                heading = stripped[level:].strip()
                headings[level - 1 :] = [heading]
            elif stripped:
                paragraph.append(stripped)
            elif paragraph:
                yield "\n".join(paragraph), tuple(headings), {"block": block}
                paragraph.clear()
                block += 1

    @staticmethod
    def _docx_blocks(
        content: bytes,
    ) -> Iterable[tuple[str, tuple[str, ...], dict[str, int | str]]]:
        headings: list[str] = []
        block = 0
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            part_names = [
                name
                for name in archive.namelist()
                if name == "word/document.xml"
                or name.startswith(("word/header", "word/footer"))
                or name in {"word/footnotes.xml", "word/endnotes.xml"}
            ]
            part_names.sort(key=lambda name: (name != "word/document.xml", name))
            for part_name in part_names:
                root = ElementTree.fromstring(archive.read(part_name))
                for paragraph in root.iter(_WORD_PARAGRAPH):
                    text = SupportedDocumentParser._docx_paragraph_text(paragraph).strip()
                    if not text:
                        continue
                    level = SupportedDocumentParser._docx_heading_level(paragraph)
                    if level is not None and part_name == "word/document.xml":
                        headings[level - 1 :] = [text]
                        continue
                    location: dict[str, int | str] = {"block": block}
                    if part_name != "word/document.xml":
                        location["part"] = part_name.removeprefix("word/")
                    heading_path = tuple(headings) if part_name == "word/document.xml" else ()
                    yield text, heading_path, location
                    block += 1

    @staticmethod
    def _docx_paragraph_text(paragraph: ElementTree.Element) -> str:
        pieces: list[str] = []

        def append_text(element: ElementTree.Element) -> None:
            for child in element:
                if child.tag == _WORD_PARAGRAPH:
                    continue
                if child.tag == _WORD_TEXT and child.text:
                    pieces.append(child.text)
                elif child.tag == _WORD_TAB:
                    pieces.append("\t")
                elif child.tag in _WORD_BREAKS:
                    pieces.append("\n")
                else:
                    append_text(child)

        append_text(paragraph)
        return "".join(pieces)

    @staticmethod
    def _docx_heading_level(paragraph: ElementTree.Element) -> int | None:
        properties = paragraph.find(f"{{{_WORD_NAMESPACE}}}pPr")
        if properties is None:
            return None
        style = properties.find(_WORD_STYLE)
        style_name = style.get(_WORD_VALUE, "") if style is not None else ""
        suffix = style_name.casefold().removeprefix("heading").strip()
        if not suffix.isdigit():
            return None
        return max(1, min(int(suffix), 9))

    @staticmethod
    def _pdf_blocks(
        content: bytes,
    ) -> Iterable[tuple[str, tuple[str, ...], dict[str, int | str]]]:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            blocks: list[tuple[str, tuple[str, ...], dict[str, int | str]]] = []
            rasterized_pages = 0
            for page_number, page in enumerate(document, start=1):
                page_area = page.rect.get_area()
                image_coverage = max(
                    (
                        rectangle.get_area() / page_area
                        for image in page.get_images(full=True)
                        for rectangle in page.get_image_rects(image)
                        if page_area > 0
                    ),
                    default=0.0,
                )
                if image_coverage >= 0.8:
                    rasterized_pages += 1
                for block_number, block in enumerate(page.get_text("blocks")):
                    text = str(block[4]).strip()
                    if text:
                        blocks.append((text, (), {"page": page_number, "block": block_number}))
            readable_words = sum(len(text.split()) for text, _, _ in blocks)
            if rasterized_pages == len(document) and readable_words < 20:
                raise DocumentParseError(
                    "PDF appears image-based but contains too little readable text; "
                    "run OCR or provide a digitally readable source so content is not lost"
                )
            yield from blocks
