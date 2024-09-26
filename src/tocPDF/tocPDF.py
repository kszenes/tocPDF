# %%
from pypdf import PdfWriter, PdfReader
import re
from tika import parser
import click
import pdfplumber
from tqdm import tqdm
from typing import Optional, List
import itertools
import tempfile

# To analyze the PDF layout and extract text
# from pdfminer.high_level import extract_pages, extract_text
# from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure


def generate_toc_pdf(filepath: str, start_toc: int, end_toc: int) -> str:
    """Creates temporary file containing only toc pages of original pdf."""
    # change numbering from math to programming
    start_toc -= 1
    end_toc -= 1

    # extract toc pages
    writer = PdfWriter()
    with open(filepath, "rb") as in_pdf:
        reader = PdfReader(in_pdf)
        for i in range(start_toc, end_toc + 1):
            page = reader.pages[i]
            writer.add_page(page)

        outpath = tempfile.NamedTemporaryFile(suffix="_toc.pdf", delete=True).name
        with open(outpath, "wb") as out_pdf:
            writer.write(out_pdf)
    return outpath


def filter_chapter(line: str) -> bool:
    """Filter checking if line corresponds to chapter in toc."""
    # check if line contains beginning or end of toc line (used for multiline chapters)
    flag_start = re.search(r"^\d+.* [A-Za-z]", line)
    flag_end = re.search(r"[A-za-z]+ \d+$", line)
    if flag_start is None and flag_end is None:
        return False
    else:
        return True


def read_toc(
    filepath: str, method: Optional[str] = "pdfplumber", debug: Optional[bool] = False
) -> List["str"]:
    """Generates a list of the table of contents using a parser method."""
    toc = []
    if method == "pdfplumber" or method is None:
        with pdfplumber.open(filepath) as f:
            # produces list of lists (each corresponding to a page)
            toc = [page.extract_text().split("\n") for page in f.pages]
            # concat lists together
            toc = list(itertools.chain.from_iterable(toc))
    elif method == "pypdf":
        toc = []
        reader = PdfReader(filepath)
        for page in reader.pages:
            raw = page.extract_text()
            toc = toc + list(filter(None, raw.split("\n")))
    elif method == "tika":
        raw = parser.from_file(filepath)
        toc = list(filter(None, raw["content"].split("\n")))
    else:
        raise Exception("Unkown method used for converting toc to list!")

    print(f"Used {method} parser for extracting table of contents.")
    if debug:
        print("\n=== Raw Parsed TOC ===\n")
        for item in toc:
            print(item + "\tpagenumber: " + item.split(" ")[-1])

    toc_only = clean_toc(toc)

    if debug:
        print("\n=== Cleaned TOC ===\n")
        for item in toc_only:
            print(item + "\tpagenumber: " + item.split(" ")[-1])
    return toc_only


def clean_toc(toc: List[str]):
    """Cleans the parsed toc from superfluous spaces and dots"""
    # Remove superfluous dots in table of contents
    toc = [re.sub(r"\s+\.*", " ", i) for i in toc]
    toc = [re.sub(r"\.*\s+", " ", i) for i in toc]
    toc = [re.sub(r"(\w)\.(?!\S)", r"\1", i) for i in toc]
    # Remove more than one successive spaces
    toc = [re.sub(r" +", r" ", i) for i in toc]
    # Remove trailing spaces
    toc = [re.sub(r" $", r"", i) for i in toc]
    # Remove lines which do not contain start or end of a multiline
    toc = list(filter(filter_chapter, toc))
    return toc


def join_multiline_sections(toc: List[str]):
    """Join multiline section titles"""
    correct_list = []
    i = 0
    while i < len(toc):
        # contains entire line
        complete_line_flag = re.search(r"^\d.* [A-Z].* \d+$", toc[i])
        if not complete_line_flag:
            # check if joined with next line completes to entire line
            if i + 1 < len(toc):
                # check if the next line is already complete
                # signifies a parsing error in the current line
                is_next_line_full = re.search(r"^\d.* [A-Z].* \d+$", toc[i + 1])
                if not is_next_line_full:
                    complete_line_flag = re.search(
                        r"^\d.* [A-Z].* \d+$", " ".join(toc[i : i + 2])
                    )
                    if complete_line_flag:
                        # if it does append
                        correct_list.append(" ".join(toc[i : i + 2]))
                        i += 1
                    else:
                        # else might be special case (e.g., annexes are numbered using letters)
                        correct_list.append(toc[i])
                else:
                    correct_list.append(toc[i])

        else:
            correct_list.append(toc[i])
        i += 1
    return correct_list


# TODO:
# - Does not support indenting instead of 1.1 (Numerical Computing)
# - Make Annex new parent chapter
def extract_toc_list_from_pdf(
    filepath: str,
    extraction_method: Optional[str] = "pdfplumber",
    debug: Optional[bool] = False,
) -> List[str]:
    """Extract list of toc (chapter name + page number) contained in temporary toc pdf"""
    # Extract text from tmp_toc.pdf, reformat and filter relevant lines
    toc_only = read_toc(filepath, extraction_method, debug)

    correct_list = join_multiline_sections(toc_only)
    if debug:
        print("\n=== Cleaned up TOC ===\n")
        for item in correct_list:
            print(item + "\tpagenumber: " + item.split(" ")[-1])
    return correct_list


def write_new_pdf_toc(
    filepath: str,
    toc: List[str],
    start_toc: int,
    offset: int,
    is_missing_pages: bool,
    reader_pdf_file=None,
    inplace: bool = False,
):
    """Generates out.pdf containing new outlined pdf."""
    if reader_pdf_file is None:
        raise Exception("pdfplumber.open() file must be provided as 6th argument")
    # change numbering from math to programming
    start_toc -= 1
    offset -= 2

    writer = PdfWriter()
    with open(filepath, "rb") as in_pdf:
        reader = PdfReader(in_pdf)
        num_pages = len(reader.pages)
        writer.append_pages_from_reader(reader)
        hierarchy = [None] * 10  # assume hierarchy does not have more than 10 levels
        writer.add_outline_item("Table of Contents", start_toc)

        # start loop over toc
        for line in tqdm(toc):
            # compute level of chapter using number of '.' in numbering (assumes format e.g. 4.2)
            level = line.split(maxsplit=1)[0].count(".")
            # Special case of header chapters with format (e.g. 4.)
            if line.split(" ", 1)[0][-1] == ".":
                level -= 1
            name, page_num_original = line.rsplit(maxsplit=1)
            try:
                page_num = offset + int(page_num_original)
            except ValueError:
                print(
                    f'Warning Parsing Error! Entry: "{name}; with page number: {page_num_original}" is not a valid page number'
                )
                print(
                    "Please enter the chapter name and page number manually or leave empty to skip entry."
                )
                new_name = input("Enter Chapter Name (leave empty to skip entry): ")
                if new_name == "":
                    print(f"Skipping entry: {name}")
                    continue
                else:
                    name = new_name
                page_num_original = int(input("Enter Page Number: "))
                page_num = page_num_original + offset

            if page_num >= num_pages:
                print(
                    f'Warning! Entry skipped: "{name} p.{page_num}" exceeds number of pages {num_pages}'
                )
                continue

            # special sections that are usually not numbered
            special_sections = [
                "Exercise",
                "Acknowledgment",
                "Reference",
                "Appendix",
                "Bibliography",
                "Further Reading",
            ]
            is_special_section = re.search(f"^({'|'.join(special_sections)})s*", name)
            if is_special_section:
                # special sections usually go under the parent
                writer.add_outline_item(name, page_num, parent=hierarchy[0])
            elif "Part" in name:
                # skip Part I, II lines
                continue
            else:
                # if missing pages set, will automatically recompute offset
                if is_missing_pages:
                    # compute new offset and page number
                    offset = recompute_offset(page_num, offset, reader_pdf_file)
                    page_num = offset + int(page_num_original)

                # add boorkmarks
                if level == 0:
                    hierarchy[level] = writer.add_outline_item(name, page_num)
                else:
                    hierarchy[level] = writer.add_outline_item(
                        name, page_num, parent=hierarchy[level - 1]
                    )

        # add _toc to filename for outplace
        outplace_path = re.sub(r"(.*/)?([^/]+)(\.pdf)", r"\1\2_toc.pdf", filepath)
        outpath = filepath if inplace else outplace_path
        with open(outpath, "wb") as out_pdf:
            print(f"\nOutlined PDF written to: {outpath}\n")
            writer.write(out_pdf)


def find_page_number(page) -> int:
    """Read the page number of a page."""
    line_list = page.extract_text().split("\n")
    # check first 3 text boxes for page number
    for i in range(min(3, len(line_list))):
        found_number = re.findall(
            r"^\d+ | \d+$", line_list[i]
        )  # number at beginning or end of line
        if found_number:
            return int(found_number[0])

    # page number not found
    return -1


def recompute_offset(page_num: int, offset: int, pdfplumber_reader) -> int:
    """Recompute offset if pdf contains missing pages between chapters."""
    additional_offset = 0
    expected_page = page_num - offset
    page_number = -1  # move to programming standard

    # extract page number from first couple of lines of pdf at corresponding page
    page = pdfplumber_reader.pages[page_num]
    page_number = find_page_number(page)

    if page_number == expected_page:
        additional_offset = 0
    else:
        # check 4 subsequent to check if compute current page number
        page_range = 10
        pages = pdfplumber_reader.pages[page_num + 1 : page_num + page_range]
        book_numbers = [page_number]
        for page in pages:
            # extract page numbers of subsequent pages
            page_number = find_page_number(page)
            book_numbers.append(page_number)

        # determine current page number by looking for consistent sequence in the following pages (e.g. book_numbers = [2, 13, 14, 15] -> page_num = 12)
        count = 0  # number of consistent numbers in book_numbers
        for i in range(len(book_numbers) - 2):
            for j in range(i + 1, len(book_numbers)):
                if book_numbers[i] == book_numbers[j] - (j - i):
                    count += 1

            # at least 2 consistent numbers need to be found for page num to be determined
            if count > 1:
                page_number = book_numbers[i] - i
                # recompute offset for mismatch in page numbers
                additional_offset = expected_page - page_number
                break
            count = 0

    if page_number == -1:
        print(f"Warning: automatic detection of offset failed for page {expected_page}")

    return offset + additional_offset


# %%

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.argument("filename")
@click.option(
    "-s",
    "--start_toc",
    required=True,
    help="PDF page number of FIRST page of Table of Contents.",
    type=int,
    prompt="Enter pdf page corresponding to FIRST page of table of contents",
)
@click.option(
    "-e",
    "--end_toc",
    required=True,
    help="PDF page number of LAST page of Table of Contents.",
    type=int,
    prompt="Enter pdf page corresponding to LAST page of table of contents",
)
@click.option(
    "-o",
    "--offset",
    required=True,
    help="Global page offset, defined as PDF page number of first page with arabic numerals.",
    type=int,
    prompt="Enter PDF page of page 1 numbered with arabic numerals. (corresponds usually to first chapter)",
)
@click.option(
    "-p",
    "--parser",
    default="pdfplumber",
    help="Parsers for extracting table of contents.",
    show_default=True,
    type=click.Choice(["pdfplumber", "pypdf", "tika"], case_sensitive=False),
)
@click.option(
    "-m",
    "--missing_pages",
    is_flag=True,
    default=False,
    help="Automatically recompute offsets by verifying book page number matches expected PDF page.",
    show_default=True,
)
@click.option(
    "-i",
    "--inplace",
    is_flag=True,
    default=False,
    help="Overwrite original PDF with new outline.",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    default=False,
    help="Outputs PDF file containing the pages provided for the table of contents.",
)
def tocPDF(filename, start_toc, end_toc, offset, parser, missing_pages, inplace, debug):
    """Generates outlined PDF based on the Table of Contents.

    Example: tocPDF -s 3 -e 5 -o 9 -p pypdf -m example.pdf"""
    filepath = filename
    outpath = generate_toc_pdf(filepath, start_toc, end_toc)
    toc = extract_toc_list_from_pdf(outpath, parser, debug)
    with pdfplumber.open(filepath) as file_reader:
        write_new_pdf_toc(
            filepath, toc, start_toc, offset, missing_pages, file_reader, inplace
        )


if __name__ == "__main__":
    tocPDF()
