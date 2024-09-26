#!/usr/bin/env python3

import os
import pypdf

from tocPDF.tocPDF import (
    clean_toc,
    filter_chapter,
    read_toc,
    generate_toc_pdf,
    join_multiline_sections,
)

HERE = os.path.abspath(os.path.dirname(__file__))


class TestTOCExtractor:
    @classmethod
    def setup_class(cls):
        cls.fpath = os.path.join(HERE, "pdfs/dotted.pdf")
        cls.outpath = generate_toc_pdf(cls.fpath, 7, 8)

    def test_toc_extraction(self):
        reader = pypdf.PdfReader(self.outpath)
        assert len(reader.pages) == 2

    def test_read_toc(self):
        toc_pypdf = read_toc(self.outpath, "pypdf")
        toc_pdfplumber = read_toc(self.outpath, "pdfplumber")
        toc_tika = read_toc(self.outpath, "tika")
        assert toc_pdfplumber == toc_pypdf
        assert toc_pdfplumber == toc_tika


class TestTOCCleaning:
    def test_join_multiline_sections(self):
        mock_toc = [
            "1 Section 1",
            "1.1 Long section",
            "that didn't fit on 1 line 2",
            "1.2 Shorter section 3",
        ]
        correct_toc = [
            "1 Section 1",
            "1.1 Long section that didn't fit on 1 line 2",
            "1.2 Shorter section 3",
        ]
        cleaned_toc = join_multiline_sections(mock_toc)
        assert correct_toc == cleaned_toc

    def test_extract_toc_list_from_pdf(self):
        moc_toc = [
            "2.4 General derivation of formal time-independent",
            "perturbation theories 29",
            "2.5 Similarity transformation derivation of the formal",
            "perturbation equations and quasidegenerate PT 46",
        ]
        correct_toc = [
            "2.4 General derivation of formal time-independent",
            "perturbation theories 29",
            "2.5 Similarity transformation derivation of the formal",
            "perturbation equations and quasidegenerate PT 46",
        ]
        cleaned_toc = clean_toc(moc_toc)
        assert correct_toc == cleaned_toc

    def test_filter_chapters(self):
        assert filter_chapter("1 Section 1") is True
        assert filter_chapter("2 Section") is True
        assert filter_chapter("Section 2") is True
        assert filter_chapter("Copyright notice") is False
        assert filter_chapter("Section on USA 3") is True
