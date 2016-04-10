from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine

from language import detect_language

#override the receive_layout method called for each page during the rendering process
class PDFPageAggregatorLineBinding(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.page_number = 0
        self.outline = False # not an outline page
        self.interesting_text = [] # filled only if there is any outline info
        self.aux_text = [] # possibly helpful info, but maybe mixed

    def receive_layout(self, ltpage):
        # this is text hacking for training purpose-> to be replaced by parsing outline
        # into dict (or else) using bboxes and page numbers
        #outline_text = [] # we will store content below contents, till end of the page
        #Hacky var
        #outline = 0

        def render(item, page_number):

            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    row = (page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str) # bbox == (x1, y1, x2, y2)
                    #  HACK
                    #check if it is outline page
                    if ('contents' in child_str.lower()):
                        #print("found", child_str.lower())
                        self.outline = True
                        self.outline = 1

                    if self.outline:

                        if ('agricultur' in child_str.lower()) or ('health' in child_str.lower())\
                           or ('social' in child_str.lower()) or ('schedule' in child_str.lower())\
                            or ('labour' in child_str.lower()) or ('revenue' in child_str.lower())\
                            or ('amendment' in child_str.lower()) or ('cancellation' in child_str.lower())\
                            or ('extension' in child_str.lower()) or ('correction' in child_str.lower()) \
                            or ('trade' in child_str.lower()) or ('industry' in child_str.lower())\
                            or ('specification' in child_str.lower()) or ('customs' in child_str.lower())\
                            or ('renewal' in child_str.lower()) or ('agreement' in child_str.lower())\
                            or ('education' in child_str.lower()) or ('regulation' in child_str.lower())\
                            or ('registration' in child_str.lower()) or ('nurse' in child_str.lower())\
                            or ('auxiliary' in child_str.lower()) or ('student' in child_str.lower())\
                            or ('benefit' in child_str.lower()) or ('act' in child_str.lower()):

                            #self.interesting_text.append(child_str.lower().rsplit()) # split by words
                            # strip '...'
                            entry = child_str.lower().replace(".","").strip()
                            language, ratio = detect_language(entry)
                            if language == 'english':

                                self.interesting_text.append(entry)

                            elif ratio['english'] > 0: # some Eng words

                                self.aux_text.append(entry)
                    # end HACK

                    self.rows.append(row)

                for child in item:
                    render(child, page_number)

            return

        render(ltpage, self.page_number)
        self.page_number += 1
        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage



# refers to the document itself:
class Issue:
  def __init__(self, publication = '', issn = 0, num_pages = 0, volume=0, gazette_title=''):
    self.publication = publication # type of gazette
    self.identifier = issn # ISSN code
    self.page_range = num_pages # number of pages
    self.edition_id = volume # volume
    self.title = gazette_title # if extraordinary

# refers to notices where the relevant data is stored: info stored in pages
#referred to in the outline + extra info on the type of data and its place on the web

class Document:
  def __init__(self, page_range = [] , uri = '', media_type = 'text' ): # media type=what typeof notice: text, jpeg
    self.page_range = page_range
    self.url = uri
    self.media_type =  media_type # {text, jpg, ...} -> some notices are Figures
