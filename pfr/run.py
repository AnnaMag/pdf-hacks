from io import StringIO
from io import BytesIO
import urllib
from urllib import request
import utils

from pdf_processing import scrape_gazette_names, get_info_outline
from data_parsing import save_to_dict



if __name__ == '__main__':
    # not saving anything locally, just the names listed on the webpage to access the files later
    url = 'http://www.gpwonline.co.za/Gazettes/Pages/Published-National-Regulation-Gazettes.aspx'


    doc_names = scrape_gazette_names(url)
    db_name = 'gov_docs'
    db_collection = 'nat_reg'

    collection = utils.set_collection(db_name, db_collection)

    for url in doc_names[0][3:5]:
            print(url)
            fp = BytesIO(urllib.request.urlopen(url).read())
            info, device, pages_skipped = get_info_outline(fp)
            print(info)
            #pages_skipped should be pages for extraction- for now is to montitore problems
            gaz_dict = save_to_dict(device.interesting_text, device.aux_text, \
                    pages_skipped, info, device.page_number, url)
            print(gaz_dict)
            utils.write_db(collection, gaz_dict)
