"""
Bill Tracker PDF Extraction Service.

Uses IBM's Docling library to extract tabular data from the
Kenya National Assembly Bills Tracker PDF and produce one
JSON record per bill.
"""
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

logger = logging.getLogger(__name__)

# ── Column name mapping ──────────────────────────────────────────────
# Maps the raw header text from the PDF table to our snake_case schema keys.
# We normalise before matching so minor whitespace / case differences are handled.
COLUMN_MAP = {
    "s/no/": "serial_number",
    "s/no": "serial_number",
    "bill": "bill",
    "sponsor": "sponsor",
    "na/sen. bill no.": "na_sen_bill_no",
    "na/sen.bill no.": "na_sen_bill_no",
    "na/sen bill no": "na_sen_bill_no",
    "dated": "dated",
    "maturity date": "maturity_date",
    "gazette no.": "gazette_no",
    "gazette no": "gazette_no",
    "1st read": "first_read",
    "2nd read": "second_read",
    "3rd read": "third_read",
    "remarks": "remarks",
    "assent": "assent",
}


def _normalise_column_name(raw: str) -> str:
    """Best-effort normalisation of a raw PDF column header."""
    cleaned = " ".join(raw.strip().lower().split())
    return COLUMN_MAP.get(cleaned, cleaned.replace(" ", "_"))


def _is_header_row(row: pd.Series) -> bool:
    """Return True if a row looks like a repeated header row."""
    values = " ".join(str(v).lower() for v in row.values if pd.notna(v))
    return "s/no" in values and "bill" in values and "sponsor" in values


def _merge_bill_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Merge consecutive rows that belong to the same bill.

    The Bills Tracker PDF often splits a single bill across multiple rows
    because of merged cells (the S/No column spans several rows).  Rows
    that belong to the same bill have NaN / empty serial_number values.
    We forward-fill the serial_number and then group-concatenate the text
    fields so each bill becomes a single record.
    """
    if df.empty:
        return []

    # Drop rows that are just repeated headers
    df = df[~df.apply(_is_header_row, axis=1)].reset_index(drop=True)

    if df.empty:
        return []

    # Forward-fill the serial_number column to associate child rows with
    # their parent bill.
    if "serial_number" in df.columns:
        df["serial_number"] = df["serial_number"].replace("", pd.NA)
        df["serial_number"] = df["serial_number"].ffill()

    # Group by serial_number and concatenate text in each field.
    text_columns = [c for c in df.columns if c != "serial_number"]
    bills: List[Dict[str, Any]] = []

    groups = df.groupby("serial_number", sort=False) if "serial_number" in df.columns else [(None, df)]

    for sno, group in groups:
        record: Dict[str, Any] = {}
        if sno is not None:
            record["serial_number"] = str(sno).strip()
        for col in text_columns:
            parts = [
                str(v).strip()
                for v in group[col]
                if pd.notna(v) and str(v).strip()
            ]
            # De-duplicate consecutive identical fragments (PDF artefacts)
            deduped: list[str] = []
            for p in parts:
                if not deduped or p != deduped[-1]:
                    deduped.append(p)
            record[col] = "; ".join(deduped) if deduped else None
        bills.append(record)

    return bills


class BillTrackerExtractor:
    """
    Extracts bill data from the National Assembly Bills Tracker PDF
    using Docling's DocumentConverter.
    """

    def __init__(self) -> None:
        logger.info("Initialising Docling DocumentConverter for Bill Tracker …")
        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
        )
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                ),
            },
        )
        logger.info("Docling DocumentConverter ready.")

    def extract(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Parse a Bills Tracker PDF and return structured JSON.

        Parameters
        ----------
        pdf_bytes : bytes
            Raw content of the uploaded PDF file.

        Returns
        -------
        dict with keys: page_count, bill_count, bills
        """
        # Write bytes to a temp file because Docling expects a file path.
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            tmp_path = Path(tmp.name)

            logger.info("Converting PDF (%d bytes) with Docling …", len(pdf_bytes))
            result = self.converter.convert(str(tmp_path))

        page_count = result.document.num_pages() if hasattr(result.document, "num_pages") else 0

        # Collect all tables from the document
        all_bills: List[Dict[str, Any]] = []

        for table_ix, table in enumerate(result.document.tables):
            logger.info("Processing table %d …", table_ix + 1)
            try:
                df = table.export_to_dataframe()
            except Exception:
                logger.warning("Failed to export table %d to DataFrame, skipping.", table_ix + 1, exc_info=True)
                continue

            if df.empty:
                continue

            # Rename columns using our mapping
            df.columns = [_normalise_column_name(str(c)) for c in df.columns]

            merged = _merge_bill_rows(df)
            all_bills.extend(merged)

        logger.info("Extraction complete: %d bills from %d pages.", len(all_bills), page_count)

        return {
            "page_count": page_count,
            "bill_count": len(all_bills),
            "bills": all_bills,
        }


# ── Singleton accessor ────────────────────────────────────────────────
_extractor_instance: BillTrackerExtractor | None = None


def get_bill_tracker_extractor() -> BillTrackerExtractor:
    """Return a shared BillTrackerExtractor instance (lazy-initialised)."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = BillTrackerExtractor()
    return _extractor_instance
