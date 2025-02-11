# tocPDF
![Tests](https://github.com/kszenes/tocPDF/actions/workflows/python-app.yml/badge.svg)

This project was created due to the lack of outlines included with most digital PDFs of textbooks.
This command line tools aims at resolving this by automatically generating the missing outline based on the table of contents.

https://github.com/user-attachments/assets/d73711d9-c236-4716-8dba-dfb4c0851722

## Installation

### PyPI

The package can be installed from PyPI:

```sh
pip install tocPDF
# although I would recommend using a tool like `pipx` or `uv tool`
# to avoid polluting your global environment
```
### Nix

There is also a Nix [package](https://search.nixos.org/packages?channel=24.11&from=0&size=50&sort=relevance&type=packages&query=tocPDF) that has been created and is maintained externally by [dansbandit](https://github.com/dansbandit) if you prefer:

```sh
nix-shell -p tocpfd
```

## Available Parsers
This package supports a number of different parsers for extracting the table of contents of from the PDF. The different parsers might yield varying results depending on the format of the table of contents. Therefore, if you are unhappy with the results of `tocPDF`, make sure to try a different parser to see if the results are improved. They can be selected using the `-p` options. The supported parsers are:
- [pdfplumber](https://github.com/jsvine/pdfplumber) (default)
- [pypdf](https://github.com/py-pdf/pypdf)
- [tika](https://github.com/chrismattmann/tika-python) (requires Java)

## Inconsistent Offset
An additional difficulty with automatically generating outlines for PDFs stems from the fact that the PDF page numbers (displayed by your PDF viewer) do not match the page numbers of the book that you are trying to outline. In addition, certain PDFs will be missing some pages (usually between root chapters) compared to the book. This means that the page difference between the book and the PDF is not consistent throughout the document and needs to be recomputed between chapters. `tocPDF` can automatically recompute this offset by comparing the expected page number to the one found in the book.

## Usage
This program requires 3 input parameters: the first and last PDF page of the table of contents as well as the PDF-book page offset. The offset is defined as the PDF page corresponding to the first book page with Arabic numerals (usually the first chapter). If your book has missing pages in between chapter, add the flag `--missing_pages`. This will dynamically adapt the page offset if there are missing pages. Note that this option will make the outline creation much more robust however the execution time will be a bit slower. If your PDF is not missing any pages you can omit this flag.
```text
$ tocPDF -h
Usage: tocPDF [OPTIONS] FILENAME

  Generates outlined PDF based on the Table of Contents.

  Example: tocPDF -s 3 -e 5 -o 9 -p pypdf -m example.pdf

Options:
  -s, --start_toc INTEGER         PDF page number of FIRST page of Table of
                                  Contents.  [required]
  -e, --end_toc INTEGER           PDF page number of LAST page of Table of
                                  Contents.  [required]
  -o, --offset INTEGER            Global page offset, defined as PDF page
                                  number of first page with arabic numerals.
                                  [required]
  -p, --parser [pdfplumber|pypdf|tika]
                                  Parsers for extracting table of contents.
                                  [default: pdfplumber]
  -m, --missing_pages             Automatically recompute offsets by verifying
                                  book page number matches expected PDF page.
  -i, --inplace                   Overwrite original PDF with new outline.
  -d, --debug                     Outputs PDF file containing the pages
                                  provided for the table of contents.
  -h, --help                      Show this message and exit.
  ```

### Example
The CLI can be simply invoked with the PDF as parameter:
```shell
tocPDF example.pdf
```
which will interactively prompt the user for the start/end pages of the PDF as well as the offset to the first page of the PDF.

These parameters can be directly provided as arguments to the CLI. For instance, the following command generates the correct outlined PDF for the example document found in `example_pdf/example.pdf`:
```shell
tocPDF --start_toc 7 --end_toc 8 --offset 9 --parser pypdf --missing_pages example.pdf
```
Or equivalently:
```shell
tocPDF -s 7 -e 8 -o 9 -p pypdf -m example.df
```
By default the outlined PDF written to `{filename}_toc.pdf`. However, it may also be performed inplace using the `-i/--inplace` flag which will overwrite the outline of the original document.

## Limitations
`tocPDF` does not support:
- scanned PDF since it does not perform OCR
- multi-column table of contents

## Alternative Software
In case the generated outline is slightly off, I recommend using the [jpdfbookmarks](https://github.com/SemanticBeeng/jpdfbookmarks) (can be directly downloaded from [sourceforge](https://sourceforge.net/projects/jpdfbookmarks/)) which is a nice piece of free software for manually editing bookmarks for PDFs.
