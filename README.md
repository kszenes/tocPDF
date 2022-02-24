# tocPDF
This project was created due to the lack of outlines included with most digital PDFs of textbooks.
This command line tools aims at resolving this by automatically generating the missing outline based on the table of contents.

## Table of Contents
- [Installation](#installation)
- [Inconsistent Offset](#inconsistent-offset)
- [Usage](#usage)
  - [Example](#example)
- [Supported Formats](#supported-formats)
- [Alternative software](#alternative-software)

## Installation

### Manual (Most Updated)
The most updated version can be downloaded by cloning the repository:

```shell
git clone https://github.com/kszenes/tocPDF.git
```

Then navigate into the base directory (toc-pdf-package) of the project and install the package using pip:

```shell
pip3 install .
```

This will fetch all the necessary dependencies for running the program as well as install the command line tool.

### PyPI (Outdated)
An outdated version has also been packaged on PyPI, however it is lacking a lot of the newer features (like `--missing_pages`). An updated version will be uploaded soon.

```shell
pip3 install tocPDF
```
## Inconsistent Offset
The main difficulty with automatically generating outlines for PDFs stems from the fact that the PDF page numbers (displayed by your PDF viewer) do not match the page numbers of the book that you are trying to outline. In addition, certain PDFs will be missing some pages (usually between root chapters) compared to the book. This means that the page difference between the book and the PDF is not consistent throughout the document and needs to be recomputed between chapters. tocPDF can automatically recompute this offset by comparing the expected page number to the one found in the book.


## Usage
This program requires 3 input parameters: the first and last PDF page of the table of contents as well as the PDF-book page offset. The offset is defined as the PDF page corresponding to the first book page with arabic numerals (usually the first chapter). If your book has missing pages in between chapter, add the flag `--missing_pages` followed by either tika or pdfplumber. This will determine the parser used to make sure that the PDF-book page offset is still correct. Note that this option will make the outline creation much more robust however the execution time will be a bit slower. If your PDF is not missing any pages you can ommit this flag.

![usage](img/usage.png)

### Example
The following command generates the correct outlined PDF for the example document that I have linked to the repository:
```shell
tocPDF -start_toc 3 -end_toc 5 -offset 9 -missing_pages tika example.pdf
```
Equivalently:

```shell
tocPDF -s 3 -e 5 -o 9 -m tika example.df
```
This will generate a new outlined PDF with the name out.pdf.

## Supported Formats

The format for table of contents varies from document to document and I can not guarantee that tocPDF will work perfectly. I have tested it out on a dozen documents and it produces decent results. Make sure to run with both parsers (`-m tika` and `-m pdfplumber`) and compare results. If you have encountered any bugs or found any unsupported table of content formats, feel free to open an issue.

## Alternative Software
In case the generated outline is slightly off, I recommend using the [jpdfbookmarks](https://github.com/SemanticBeeng/jpdfbookmarks) (can be directly donwloaded from [sourceforge](https://sourceforge.net/projects/jpdfbookmarks/)) which is a nice piece of free software for manually editing bookmarks for PDFs.



