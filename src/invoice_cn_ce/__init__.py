"""invoice_cn_ce — electronic invoice field extractor (PDF + XML).

Public API:
    parse_pdf(contents, filename="") -> ExtractResponse
    InvoiceRecord, PdfRaw, ExtractResponse        — data models
    Settings, settings                            — configuration

The CLI surface lives in :mod:`invoice_cn_ce.cli` (console script ``invoice_cn_ce``) and
:mod:`invoice_cn_ce.server` (console script ``invoice_cn_ce-server``).
"""

from __future__ import annotations

from .config import Settings, settings
from .formats import parse_pdf
from .schemas import ExtractResponse, InvoiceRecord, PdfRaw

__all__ = [
    "parse_pdf",
    "InvoiceRecord",
    "PdfRaw",
    "ExtractResponse",
    "Settings",
    "settings",
]