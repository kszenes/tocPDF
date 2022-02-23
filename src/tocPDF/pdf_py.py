#%%
from PyPDF2 import PdfFileWriter, PdfFileReader
import re
from tika import parser
import click
import pdfplumber
import os
from tqdm import tqdm
from typing import Optional, List
import itertools

def generate_toc_pdf(filepath: str, start_toc: int, end_toc: int) -> str:
  """Creates tmp_toc.pdf containing only toc pages of original pdf."""
  # change numbering from math to programming
  start_toc -= 1
  end_toc -= 1

  # extract toc pages
  writer = PdfFileWriter()
  with open(filepath, 'rb') as in_pdf:
    reader = PdfFileReader(in_pdf)
    for i in range(start_toc, end_toc+1):
      page = reader.getPage(i)
      writer.addPage(page)
    
    outpath = "tmp_toc.pdf"
    with open(outpath, 'wb') as out_pdf:
      writer.write(out_pdf)
  return outpath

def filter_chapter(line: str) -> bool:
  """Filter checking if line corresponds to chapter in toc."""
  # check if line contains beginning or end of toc line (used for multiline chapters)
  flag_start = re.search(r'^\d+.* [A-Z]', line) 
  flag_end = re.search(r'[a-z]+ \d+$', line)
  if flag_start is None and flag_end is None:
    return False
  else:
    return True

def read_toc(filepath: str, method: Optional[str] = 'pdfplumber') -> List['str']:
  """Generates a list of the table of contents using a parser method. """
  toc = ''
  if method == 'pdfplumber':
    with pdfplumber.open('tmp_toc.pdf') as f:
      # produces list of lists (each corresponding to a page)
      toc = [page.extract_text().split('\n') for page in f.pages]
      # concat lists together
      toc = list(itertools.chain.from_iterable(toc))
  elif method == 'tika':
    raw = parser.from_file(filepath)
    toc = list(filter(None, raw['content'].split('\n')))
  else:
    raise Exception('Unkown method used for converting toc to list!')
    
  print(f'Used {method} for converting table of content to list.')
  # Cleaning up toc
  toc_clean = [re.sub(r'(\.){2,}| \.| ·|', '', i) for i in toc]
  toc_clean = [re.sub(r'(\w)\.(?!\S)', r'\1', i)for i in toc_clean]
  toc_clean = [re.sub(r' +', r' ', i)for i in toc_clean]
  toc_clean = [re.sub(r' $', r'', i)for i in toc_clean]
  toc_only = list(filter(filter_chapter, toc_clean))
  return toc_only

# TODO:
# Does not support format Chapter 3 ..... 12 (LEVEQUE 1990) (use tabula?)
# Does not support inenting instead of 1.1 (Numerical Computing)
# Make Annex new parent chapter
def extract_toc_list_from_pdf(filepath: str, extraction_method: Optional[str] = 'tika', debug: Optional[bool] =False,) -> List[str]:
  """Extract list of toc (chapter name + page number) contained in tmp_toc.pdf"""
  # Extract text from tmp_toc.pdf, reformat and filter relevant lines
  toc_only = read_toc(filepath, extraction_method)

  # -begin: join multilined chapters into 1-
  correct_list = []
  i = 0
  while i < len(toc_only):
    # contains entire line
    complete_line_flag = re.search(r'^\d.* [A-Z].* \d', toc_only[i])
    if complete_line_flag is None:
      # check if joined with next line completes to entire line
      complete_line_flag = re.search(r'^\d.* [A-Z].* \d', ' '.join(toc_only[i:i+2]))
      if complete_line_flag is not None:
        # if it does append
        correct_list.append(' '.join(toc_only[i:i+2]))
        i += 1 
      else:
        # else might be special case (e.g annexes are numbered using letters)
        correct_list.append(toc_only[i])
    else:
      correct_list.append(toc_only[i])
    i += 1
  # -end: join multilined chapters into 1-

  # if debug set, does not automatically erase tmp_toc.pdf
  if debug == False:
    if os.path.exists(filepath):
      os.remove(filepath)
    else:
      print('Warning: tmp_toc.pdf not deleted.')
  return correct_list

def write_new_pdf_toc(filepath: str, toc: List[str], start_toc: int, offset: int, missing_pages: str, reader_pdf_file=None, chapter_offset: Optional[int]=0):
  """Generates out.pdf containing new outlined pdf."""
  if reader_pdf_file is None:
    raise Exception('pdfplumber.open() file must be provided as 6th argument')
  # change numbering from math to programming
  start_toc -= 1
  offset -= 2

  writer = PdfFileWriter()
  with open(filepath, 'rb') as in_pdf:
    reader = PdfFileReader(in_pdf)
    num_pages = reader.numPages
    writer.appendPagesFromReader(reader)
    hierarchy = [None] * 10 # assume hierarchy does not have more than 10 levels
    writer.addBookmark('Table of Contents', start_toc)

    # start loop over toc
    for line in tqdm(toc):
      # compute level of chapter using number of '.' in numbering (assumes format e.g. 4.2)
      level = line.split(maxsplit=1)[0].count('.')
      # Special case of header chapters with format (e.g. 4.)
      if line.split(' ', 1)[0][-1] == '.':
        level -= 1
      name, page_num_original = line.rsplit(maxsplit=1)
      page_num = offset + int(page_num_original)

      if page_num >= num_pages:
        print(f'Warning! Entry skipped: "{name} p.{page_num}" exceeds number of pages {num_pages}')
        continue

      if 'Exercise' in name:
        # exercises usually go under the parent 
        writer.addBookmark(name, page_num, parent=hierarchy[0])
      elif 'Part' in name:
        # skip Part I, II lines
        continue
      else:
        # if missing pages set, will automatically recompute offset
        if missing_pages:
          # compute new offset and page number
          offset = recompute_offset(page_num, offset, reader_pdf_file)
          page_num = offset + int(page_num_original)

        # add boorkmarks
        if level == 0:
            hierarchy[level] = writer.addBookmark(name, page_num)
        else:
          hierarchy[level] = writer.addBookmark(
                name, page_num, parent=hierarchy[level-1])

    # write out.pdf file
    with open('./out.pdf', 'wb') as out_pdf:
      print('outlined PDF written to out.pdf')
      writer.write(out_pdf)


def recompute_offset(page_num: int, offset: int, pdfplumber_reader) -> int:
  """Recompute offset if pdf contains missing pages between chapters."""
  additional_offset = 0
  expected_page = page_num - offset
  page_number = -1 # move to programming standard

  # extract page number from first line of pdf at corresponding page
  page = pdfplumber_reader.pages[page_num]
  line_list = page.extract_text().split('\n')
  found_number = re.findall('^\d+|\d+$', line_list[0]) # number at beginning or end of line

  # if number found convert to int
  if found_number:
    page_number = int(found_number[0])

  if page_number == expected_page:
    additional_offset = 0
    pass
  else:
    # check 4 subsequent to check if compute current page number
    page_range = 10
    pages = pdfplumber_reader.pages[page_num+1:page_num+page_range]
    book_numbers = [page_number]
    for page in pages:
      # extract page numbers of subsequent pages
      line_list = page.extract_text().split('\n')
      found_number = re.findall('^\d+ | \d+$', line_list[0])
      if found_number:
        found_number = int(found_number[0])
      else:
        found_number = -1

      book_numbers.append(found_number)

    # determine current page number by looking for consistent sequence in the following pages (e.g. book_numbers = [2, 13, 14, 15] -> page_num = 12)
    # print(book_numbers)
    count = 0 # number of consistent numbers in book_numbers
    for i in range(len(book_numbers)-2):
      for j in range(i+1, len(book_numbers)):
        if book_numbers[i] == book_numbers[j] - (j-i):
          count += 1
      
      # at least 2 consistent numbers need to be found for page num to be determined
      if count > 1:
        page_number = book_numbers[i] - i
        # recompute offset for mismatch in page numbers
        additional_offset = expected_page - page_number
        break
      count = 0

  if page_number == -1:
    print(f'Warning: automatic detection of offset failed for page {expected_page}')

  return offset + additional_offset

# %%

# === Relativistic Quantum Chemistr ===
# filepath = '/Users/kalmanszenes/code/tocPDF-package/example_pdf/Relativistic_Quantum_Chemistry.pdf'
# outpath = generate_toc_pdf(filepath, 6, 18)
# toc = extract_toc_list_from_pdf(outpath, debug=True, extraction_method='tika')
# print(f'Opening {filepath} with pdfplumber')
# with pdfplumber.open(filepath) as file_reader:
#   print(f'PDF successfully opened.')
#   write_new_pdf_toc(filepath, toc, 6, 24, True, file_reader)
# === End ===

# === Leveque 1990 ===
filepath = '/Users/kalmanszenes/My Drive/Textbooks/pdf_toc/LEVEQUE1990_Book_NumericalMethodsForConservatio.pdf'
outpath = generate_toc_pdf(filepath, 5, 8)
toc = extract_toc_list_from_pdf(outpath, extraction_method='pdfplumber',debug=True)
print(f'Opening {filepath} with pdfplumber')
with pdfplumber.open(filepath) as file_reader:
  print(f'PDF successfully opened.')
  write_new_pdf_toc(filepath, toc, 6, 10, True, file_reader)
# === End ===

# # === Discontinuous Galerkin ===
# filepath = '/Users/kalmanszenes/code/tocPDF-package/example_pdf/DiscontinuousGalerkin.pdf'
# outpath = generate_toc_pdf(filepath, 10, 13)
# toc = extract_toc_list_from_pdf(outpath, extraction_method='tika', debug=True)
# with pdfplumber.open(filepath) as file_reader:
#   print(f'pdfplumber opened file')
#   write_new_pdf_toc(filepath, toc, 10, 14, 1, file_reader)
# === End===

# === Bayesian ===
# filepath = '/Users/kalmanszenes/My Drive/Textbooks/bayesian_data.pdf'
# outpath = generate_toc_pdf(filepath, 10, 13)
# toc = extract_toc_list_from_pdf(outpath, extraction_method='pdfplumber', debug=True)
# with pdfplumber.open(filepath) as file_reader:
#   print(f'pdfplumber opened file')
#   write_new_pdf_toc(filepath, toc, 10, 14, 1, file_reader)
# === End ===
#%%
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('filename')
@click.option('-s', '--start_toc', required=True, help='Page number of pdf for the first page of the table of contents.', type=int, prompt='Enter pdf page corresponding to FIRST page of table of contents')
@click.option('-e', '--end_toc', required=True, help='Page number of pdf for the last page of the table of contents.', type=int, prompt='Enter pdf page corresponding to LAST page of table of contents')
@click.option('-o', '--offset', required=True, help='Offset for pdf. Defined as pdf page number of first chapter.',  type=int, prompt='Enter pdf page corresponding to first arabic numeral (usually first chapter)')
@click.option('-m', '--missing_pages', default=None, help='(EXPERIMENTAL) tika [default] or pdfplumber', show_default=True)
@click.option('-c', '--chapter_offset', default=0, help='Certain pdfs have additional offsets at each chapter. (EXPERIMENTAL)', type=int, show_default=True)
@click.option('-d', '--debug', default=False, help="Outputs separate pdf file (filename_toc.pdf) containing the pages provided for the table of contents. (used for debugging)", show_default=True)
def toc_pdf(filename, start_toc, end_toc, offset, missing_pages, chapter_offset, debug):
  """Creates a new pdf called out.pdf with an outline generated from the table of contents.
  
  FILENAME is the pdf file to be outlined."""
  filepath = './' + filename
  outpath = generate_toc_pdf(filepath, start_toc, end_toc)  
  toc = extract_toc_list_from_pdf(outpath, missing_pages, debug)
  with pdfplumber.open(filepath) as file_reader:
    write_new_pdf_toc(filepath, toc, start_toc, offset, missing_pages, file_reader) 


if __name__ == '__main__':
  toc_pdf()


# %%

  


# %%
