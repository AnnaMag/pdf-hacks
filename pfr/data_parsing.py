import json, re, time

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

                if ('no' in x):
                    num = re.search(r'[A-Za-z]{2}[.][ ]\d{1,}', x, re.IGNORECASE).string.split(' ')

                    uid_no = num[1]
                    # to fix! sometimes there are 2 numer references, so we store the 2nd

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



def save_to_json(notice_info, notice_subject, pages_to_extract, classification_data, num_pages, url):
            """
            classification_data: data about the document (date, vol, number, title)
            pages_to_extract: where the info is
            notice_info: what the notice is about, fetched from the 'outline'
            """
            from collections import defaultdict
            classification = defaultdict(list) # dict to store data and dump into json

            classification['issue'] = Issue() # instance of Issue
            # publication = '', issn = 0, num_pages = 0, volume=0, notice_title='')

            classification['document'] = Document() # instance of Document- mainly to gather
               # pages where notices are published and their types

            classification['url'] = url

            for x in set(classification_data):
                if ('vol' in x):
                    uid_vol = x.split('.')[1].strip()

                    classification['issue'].edition_id = uid_vol

                # sometimes there are 2 numer references
                if ('no' in x):
                    x = re.search(r'[A-Za-z]{2}[.][ ]\d{1,}', info[1], re.IGNORECASE).string.split(' ')

                    uid_no = x[1]
                    classification['other_attributes'].append(uid_no)

                if ('gazette' in x):
                    classification['issue'].publication = x
                    uid_type = x

                if ('province' in x):
                    classification['other_attributes'].append(x)

                if ('extraordinary' in x):
                    classification['issue'].title = 'extraordinary'

                if ('issn' in x):
                    # save just the number
                    classification['issue'].identifier = x.split('issn ')[1].strip()

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

            classification['document'].page_range =  pages_to_extract
            classification['subjects'] = notice_subject # entities
            classification['about'] = [] # parsed info

            classification['issue'].page_range = num_pages

            # timestamp of accessing the doc
            classification['other_attributes'].append(time.asctime( time.localtime(time.time()) ))

            #classification['source_url'] =

            uid = uid_no + '_' + uid_vol
            # modify id's if necessary
            classification['uid'] = uid # must be unique
            classification['identifier'] = uid  # + uid_type ? can be more descriptive possibly

            # see comment above this function
            return json.dumps(classification, default=lambda o: o.__dict__, sort_keys=True)#, indent=4)
