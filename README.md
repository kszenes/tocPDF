# tocPDF
This project was created due to the lack of outlines included with most digital PDFs of textbooks.
This command line tools aims at resolving this by automatically generating the missing outline based on the table of contents.

## Table of contents
- [tocPDF](#tocpdf)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Example](#example)
  - [Known issues](#known-issues)
  - [Alternative software](#alternative-software)
  - [Upcoming features](#upcoming-features)

## Installation
The most updated version can be downloaded by cloning the repository:

```shell
git clone https://github.com/kszenes/tocPDF.git
```

Then navigate into the base directory (toc-pdf-package) of the project and install the package using pip:

```shell
pip3 install .
```

This will fetch all the necessary dependencies for running the program as well as install the command line tool.

The program is also packaged on PyPI but the version is very outdated. (Will be updated soon)

```shell
pip3 install tocPDF
```


## Usage
The program must be provided with the path to the PDF file that you wish to bookmark as well as the first and last page of the table of contents in the book.
These pages will be read by the program to generate the outline.
Finally, the offset must be provided.
The offset is defined as the PDF page number of the first page of the book numbered using arabic numerals (e.g. 1, 2, 3...).
This usually corresponds to the first chapter of the book (excluding the Preface).

![usage](img/usage.png)

### Example
Here is an example command:
```shell
tocPDF -file example.pdf -start_toc 8 -end_toc 14 -offset 21
```
Equivalently:

```shell
tocPDF -f example.pdf -s 8 -e 14 -o 21
```
This will generate two PDFs: example_toc.pdf and out.pdf. The former is a auxiliary file that is used for debugging. If you encounter an issue, make sure to verify that this file only contains the pages corresponding to the table of contents in the PDF. The latter is the original PDF with the added outline.

## Known issues
1. Some PDFs contain missing pages usually between the root chapters. If it is consistently the same number of pages (e.g. 1 or 2) this can be specified using the optionnal argument -chapter_offset.
2. tocPDF assumes that the way that subchapters is defined using a dot separator (e.g. Chapter 4: Subchapter 3 is 4.3). Under the hood, tocPDF counts the number of dots in the string to determine the hierarchy. If the PDF does not follow this convention, tocPDF will fail to identify the correct outline. Note that this only affects the outline hierarchy while the bookmark locations might still be correct.

The code is in early development so please feel free to open an issue if you find any additional bugs or features that you would like to be added.

## Alternative software
In case the generated outline is slightly off, I recommend using the [jpdfbookmarks](https://github.com/SemanticBeeng/jpdfbookmarks) (can be directly donwloaded from [sourceforge](https://sourceforge.net/projects/jpdfbookmarks/)) which is a nice piece of free software for manually editing bookmarks for PDFs.

## Upcoming features
- Fix the first issue mentioned here above.
- Provide option to automatically delete temporary table of contents PDF copy generated.


