#!/usr/bin/env python3

import os
import pypdf

from tocPDF.tocPDF import clean_toc, read_toc, generate_toc_pdf, join_multiline_sections

HERE = os.path.abspath(os.path.dirname(__file__))


class TestTOCExtractor:
    @classmethod
    def setup_class(cls):
        print(f"{os.listdir(HERE) = }")
        print(f"{os.listdir(os.path.join(HERE, 'pdfs')) = }")
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
    def test_clean_toc(self):
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

    def test_extract_toc_list_from_pdf(self):
        moc_toc = [
            "1 Section                 1",
            "2 Section                 2   ",
            "3 Section ................................... 3",
            "4 Section . . . . . . . . 4",
            "5 Section . . . . . . . .5",
            "6 Section. . . . . . . . 6",
            "7 Section. . . . . . . .7",
        ]
        correct_toc = [
            "1 Section 1",
            "2 Section 2",
            "3 Section 3",
            "4 Section 4",
            "5 Section 5",
            "6 Section 6",
            "7 Section 7",
        ]
        cleaned_toc = clean_toc(moc_toc)
        assert correct_toc == cleaned_toc
