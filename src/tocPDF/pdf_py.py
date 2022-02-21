#%%
from PyPDF2 import PdfFileWriter, PdfFileReader
import re
from tika import parser
import click

def generate_toc_pdf(filepath, start_toc, end_toc):
  writer = PdfFileWriter()
  with open(filepath, 'rb') as in_pdf:
    reader = PdfFileReader(in_pdf)
    for i in range(start_toc, end_toc+1):
      page = reader.getPage(i)
      writer.addPage(page)
    
    outpath = filepath.rsplit('.', 1)[0] + '_toc.pdf'
    with open(outpath, 'wb') as out_pdf:
      writer.write(out_pdf)
      return outpath

def filter_chapter(line):
  flag_start = re.search(r'^\d+.* [A-Z]', line)
  flag_end = re.search(r'[a-z]+ \d+$', line)
  if flag_start is None and flag_end is None:
    return False
  else:
    return True

def extract_toc_list_from_pdf(filepath):
  raw = parser.from_file(filepath)
  toc = list(filter(None, raw['content'].split('\n')))
  toc_clean = [i.replace(' .', '') for i in toc]
  toc_only = list(filter(filter_chapter, toc_clean))
  # fix for 2 lined chapters
  correct_list = []
  i = 0
  while i < len(toc_only):
    complete_line_flag = re.search(r'^\d.* [A-Z].* \d', toc_only[i])
    if complete_line_flag is None:
      complete_line_flag = re.search(r'^\d.* [A-Z].* \d', ' '.join(toc_only[i:i+2]))
      if complete_line_flag is not None:
        correct_list.append(' '.join(toc_only[i:i+2]))
        i += 1 
      else:
        correct_list.append(toc_only[i])
    else:
      correct_list.append(toc_only[i])
    i += 1
  return correct_list

def write_new_pdf_toc(filepath, toc, start_toc, offset, chapter_offset):
  writer = PdfFileWriter()
  with open(filepath, 'rb') as in_pdf:
    reader = PdfFileReader(in_pdf)
    num_pages = reader.numPages
    writer.appendPagesFromReader(reader)


    hiearchy = [None] * 10
    writer.addBookmark('Table of Contents', start_toc)

    shift = 0
    for line in toc:
      level = line.split(' ', 1)[0].count('.')
      name, page_num_original = line.rsplit(' ', 1)
      page_num = offset + int(page_num_original) - shift * chapter_offset
      # page_num = offset + int(page_num)
      if page_num >= num_pages:
        print(f'Warning! Entry skipped: "{name} p.{page_num}" exceeds number of pages {num_pages}')
        continue
      if 'Exercise' in name:
          writer.addBookmark(name, page_num, parent=hiearchy[0])
      elif 'Part' in name:
        continue
      else:
        if level == 0:
            if hiearchy[level] is not None:
              shift += 1
              page_num = offset + int(page_num_original) - shift * chapter_offset
            hiearchy[level] = writer.addBookmark(name, page_num)
        else:
            hiearchy[level] = writer.addBookmark(
                name, page_num, parent=hiearchy[level-1])


    with open('./out.pdf', 'wb') as out_pdf:
      writer.write(out_pdf)

# %%

# outpath = generate_toc_pdf('./LEVEQUE_EXTENDED.pdf', 8, 15)
# toc = extract_toc_list_from_pdf(outpath)
# write_new_pdf_toc(toc, 8, 19)

# outpath = generate_toc_pdf('./Relativistic_Quantum_Chemistry.pdf', 6-1, 18-1)
# toc = extract_toc_list_from_pdf(outpath)
# write_new_pdf_toc('./Relativistic_Quantum_Chemistry.pdf', toc, 6-1, 24-2, 1)

# outpath = generate_toc_pdf('./DiscontinuousGalerkin.pdf', 10-1, 13-1)
# toc = extract_toc_list_from_pdf(outpath)
# write_new_pdf_toc('./DiscontinuousGalerkin.pdf', toc, 10-1, 14-2, 1)
#%%

@click.command()
@click.option('-f', '--file', required=True, help='Filename of pdf.')
@click.option('-s', '--start_toc', required=True, help='Page number of pdf for the first page of the table of contents.', type=int)
@click.option('-e', '--end_toc', required=True, help='Page number of pdf for the last page of the table of contents.', type=int)
@click.option('-o', '--offset', required=True, help='Offset for pdf. Defined as pdf page number of first chapter.',  type=int)
@click.option('-c', '--chapter_offset', default=0, help='Certain pdfs have additional offsets at each chapter. (EXPERIMENTAL)', type=int)
def toc_pdf(file, start_toc, end_toc, offset, chapter_offset):
  """Creates a new pdf called out.pdf with an outline generated from the table of contents."""
  filepath = './' + file
  outpath = generate_toc_pdf(filepath, start_toc-1, end_toc-1)  
  toc = extract_toc_list_from_pdf(outpath)
  write_new_pdf_toc(filepath, toc, start_toc-1, offset-2, chapter_offset)


if __name__ == '__main__':
  toc_pdf()


# %%

  


# %%
