# tocPDF
This project was created due to the lack of outlines included with most digital PDFs of textbooks.
This command line tools aims at resolving this by automatically generating the missing outline based on the table of contents.

## Table of Contents
- [tocPDF](#tocpdf)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [PIP](#pip)
    - [Manually](#manually)
  - [Inconsistent Offset](#inconsistent-offset)
  - [Usage](#usage)
    - [Example](#example)
  - [Supported Formats](#supported-formats)
  - [Alternative Software](#alternative-software)

## Installation

### PIP

The package can be downloaded using pip:

```shell
pip install tocPDF
```

### Manually
It can be installed manually by first cloning the repository:

```shell
git clone https://github.com/kszenes/tocPDF.git
```

Then navigate into the base directory (toc-pdf-package) of the project and install the package using pip:

```shell
pip install .
```

This will fetch all the necessary dependencies for running the program as well as install the command line tool.

## Inconsistent Offset
The main difficulty with automatically generating outlines for PDFs stems from the fact that the PDF page numbers (displayed by your PDF viewer) do not match the page numbers of the book that you are trying to outline. In addition, certain PDFs will be missing some pages (usually between root chapters) compared to the book. This means that the page difference between the book and the PDF is not consistent throughout the document and needs to be recomputed between chapters. tocPDF can automatically recompute this offset by comparing the expected page number to the one found in the book.


## Usage
This program requires 3 input parameters: the first and last PDF page of the table of contents as well as the PDF-book page offset. The offset is defined as the PDF page corresponding to the first book page with Arabic numerals (usually the first chapter). If your book has missing pages in between chapter, add the flag `--missing_pages` followed by either tika or pdfplumber. This will determine the parser used to make sure that the PDF-book page offset is still correct. Note that this option will make the outline creation much more robust however the execution time will be a bit slower. If your PDF is not missing any pages you can omit this flag.

```sh
Usage: tocPDF [OPTIONS] FILENAME

  Generates outlined PDF based on the Table of Contents. Version: 0.3.1

  Example: tocPDF example.pdf

Options:
  -s, --start_toc INTEGER   PDF page number of FIRST page of Table of
                            Contents.  [required]
  -e, --end_toc INTEGER     PDF page number of LAST page of Table of Contents.
                            [required]
  -o, --offset INTEGER      Global page offset, defined as PDF page number of
                            first page with arabic numerals.  [required]
  -m, --missing_pages TEXT  Parser (tika or pdfplumber) used to automatically
                            detect offset by verifying book page number
                            matches expected PDF page.
  -d, --debug               Outputs PDF file (tmp_toc.pdf) containing the
                            pages provided for the table of contents.
  -h, --help                Show this message and exit.
```


### Example
The CLI can be simply invoked with the PDF as parameter:
```shell
tocPDF example.pdf
```
and then the user will be prompted to add the start/end pages of the PDF as well as the offset to the first page of the PDF.

These parameters can be directly provided as arguments to the CLI. For instance, the following command generates the correct outlined PDF for the example document found in `example_pdf/example.pdf`:
```shell
tocPDF --start_toc 3 --end_toc 5 --offset 9 --missing_pages tika example.pdf
```
Or equivalently:
```shell
tocPDF -s 3 -e 5 -o 9 -m tika example.df
```
This will generate a new outlined PDF with the name out.pdf.

## Supported Formats

The format for table of contents varies from document to document and I can not guarantee that tocPDF will work perfectly. I have tested it out on a dozen documents and it produces decent results. Make sure to run with both parsers (`-m tika` and `-m pdfplumber`) and compare results. If you have encountered any bugs or found any unsupported table of content formats, feel free to open an issue.

## Alternative Software
In case the generated outline is slightly off, I recommend using the [jpdfbookmarks](https://github.com/SemanticBeeng/jpdfbookmarks) (can be directly downloaded from [sourceforge](https://sourceforge.net/projects/jpdfbookmarks/)) which is a nice piece of free software for manually editing bookmarks for PDFs.



