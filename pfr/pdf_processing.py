from pyquery import PyQuery as pq
from lxml import etree
import urllib
from urllib import request
import re

from PyPDF2 import PdfFileWriter, PdfFileReader

from classes import PDFPageAggregatorLineBinding
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams


# Cast to StringIO object- adjustment for Python3
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from io import BytesIO

#extract url's
def process_url(url, page_no):

    end_reading = 1

    d = pq(url, opener=lambda url, **kw: urllib.request.urlopen(url).read().decode('latin1'))
    # grep all the Gazette classes
    gt = d('div').filter('.GazetteTitle')

    if (gt != []): # some pages can be empty when done iterating, so if there is anything at all
        # so there is sth on the page. we need to still check whether the page requested
        # corresponds to the one indicated by the bottom bar ('strong' label)
        curr_page = int(d('div').filter('.Paging').find('strong').text())

        if curr_page != page_no:
            # we cycled back to the beg page = end the crawl
            end_reading = 0

            return [], end_reading # crawl is over

        else:

            return [gt(x).eq(0).find('a').attr('href') for x in gt], end_reading

    else:

        end_reading = 0
        return [], end_reading # crawl is over

def scrape_gazette_names(url_sub):
    page_no = 0
    to_end = 1
    gazette_names = []
    try:
        while (to_end):

            page_no += 1
            url= url_sub + '?p=' + str(page_no)

            #url='http://www.gpwonline.co.za/Gazettes/Pages/Published-Tender-Bulletin.aspx?p=' \
            #+ str(page_no)

            names_extracted, to_end = process_url(url, page_no)

            if to_end: # finish the parsing

                gazette_names.append(names_extracted)

            else:
                pass

    except urllib.request.HTTPError as e: # bad url-> 404
            print('HTTP ERROR %s: no webpage' % e.code)
            pass # no more webpages - assumes that no pages are broken in the middle
    return gazette_names

def extract_gazette_info(dev_info):

    class_info = []

    for i in range(len(dev_info)):

        entry = dev_info[i][-1].replace('\n','').lower()
        if ('issn' in entry) or ('vol.' in entry) or ('province' in entry) \
            or ('regulation' in entry) or ('extraord' in entry):

            class_info.append(entry)

        if 'no.' in entry: # sometimes no. belongs to unrelated entires
                x = re.search(r'^no[.][ ]\d{1,}$', entry, re.IGNORECASE)#.string#.split(' ')
                if x:
                    #print('no...', x.string)
                    class_info.append(x.string)

        try:
            date_re = re.search(r'\d{1,}[ ][A-Za-z]{3,}[ ]\d{4}', entry, re.IGNORECASE).string#.split(' ')
            if date_re and ('gazette' in date_re):
                    date = date_re.split(',')

                    class_info.append(date[0])
                    class_info.append(date[1])

        except:
            pass

    return class_info



def get_info_outline(fp):
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregatorLineBinding(rsrcmgr, laparams=laparams) # adds information from pages
              # =  cumulates text per pages read
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    dev_info = [] # first 2 pages
    info = [] # issue info
    skip = 0 # to skip pages with extra complex background
    pages_skipped = []

    for i, page in enumerate(PDFPage.create_pages(doc)):
            try:
                page.resources['ColorSpace']
                skip = 1
            except:
                #print('no CS field')
                skip = 0
                pages_skipped.append(i)
                pass

            if not skip:
                interpreter.process_page(page)
                device.get_result()

                if i ==0 or i == 1:  # device cumulates output, so this is p1 and p2 (0+1)
                        # the reason for 'or' is that the 2nd page might be contaminated
                        # in which case onky the front is used
                        # receive the LTPage object for this page
                        dev_info = device.rows

                if device.outline: # stop scan after seeing the outline

                        break


    info = extract_gazette_info(dev_info)
    return info, device, pages_skipped


# split pdf
def split_pdf(input_pdf, list_pages, end_page = None):

        res = []
        if not end_page:
            end_page = inputpdf.numPages

        for i in range(len(list_pages)):

            output_i = PdfFileWriter()

            if i == len(list_pages)-1:
                end = end_page -1
            else:
                end = list_pages[i+1] -1

            for j in range(list_pages[i], end):
                output_i.addPage(inputpdf.getPage(j))
            #with open("document-page%i.pdf" % i, "wb") as outputStream:
             #   output_i.write(outputStream)

            sio = BytesIO()
            output_i.write(sio)

            res.append(sio)

        return res
