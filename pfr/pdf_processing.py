from pyquery import PyQuery as pq
from lxml import etree
import urllib
from urllib import request

from PyPDF2 import PdfFileWriter #  PdfFileReader ?


# Cast to StringIO object- adjustment for versioning of Python
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from io import BytesIO

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

def save_to_dict(notice_info, notice_subject, pages_to_extract, classification_data, num_pages, url):
        """
        same as save_to_json, but stopped at the dict form
        """
        #from collections import defaultdict
        classification = dict() # dict to store data and dump into json

        # this one will be a list of extra info
        classification['other_attributes'] = []

        classification['issue'] = dict()#Issue() # instance of Issue
        # publication = '', issn = 0, num_pages = 0, volume=0, notice_title='')

        classification['document'] = dict() #Document() # instance of Document- mainly to gather
           # pages where notices are published and their types

        classification['url'] = url

        for x in set(classification_data):
            if ('vol' in x):
                uid_vol = x.split('.')[1].strip()

                classification['issue']['edition_id'] = uid_vol

            # sometimes there are 2 numer references
            if ('no' in x):
                x = re.search(r'[A-Za-z]{2}[.][ ]\d{1,}', info[1], re.IGNORECASE).string.split(' ')

                uid_no = x[1]
                classification['other_attributes'].append(uid_no)

            if ('gazette' in x):
                classification['issue']['publication'] = x
                uid_type = x

            if ('province' in x):
                classification['other_attributes'].append(x)

            if ('extraordinary' in x):
                classification['issue']['title'] = 'extraordinary'

            if ('issn' in x):
                # save just the number
                classification['issue']['identifier'] = x.split('issn ')[1].strip()

            #date
            try:

                date_re = re.search(r'\d{1,}[ ][A-Za-z]{3,}[ ]\d{4}', x, re.IGNORECASE).string.lstrip().split(' ')
                classification['date_published'] = [date_re[1],date_re[2]]
                classification['other_attributes'].append(date_re[0] + ' / ' + date_re[1] + ' / ' + date_re[2])

            except:
                pass

        # add info from the outline (keywords are important)
        # shoulf be parsed: save keywords?
        classification['summary'] = notice_info

        # page_range, string /^[0-9]*(-[0-9]*)?$/
        # The pages the document within the issue where to look for info

        classification['document']['page_range'] =  pages_to_extract
        classification['subjects'] = notice_subject # entities
        classification['about'] = [] # parsed info

        classification['issue']['page_range'] = num_pages

        # timestamp of accessing the doc
        classification['other_attributes'].append(time.asctime( time.localtime(time.time()) ))

        #classification['source_url'] =

        uid = uid_no + '_' + uid_vol
        # modify id's if necessary
        classification['uid'] = uid # must be unique
        classification['identifier'] = uid  # + uid_type ? can be more descriptive possibly

        # see comment above this function
        return classification


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
