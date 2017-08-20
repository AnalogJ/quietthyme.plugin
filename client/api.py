__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

import sys
import json
import os
import logging
from calibre_plugins.quietthyme.client.requestmanager import RequestManager

class ApiClient():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # def auth(self, library_uuid, library_name):
    #     """
    #     This function will authenticate with Quietthyme and generate a JWT for subsequent api calls.
    #     :param library_uuid: calibre library identifier
    #     :return: quietthyme jwt.
    #     """
    #     self.logger.debug(sys._getframe().f_code.co_name)
    #
    #     if not library_uuid:
    #         return {'success': False, 'error_msg': 'No library uuid found'}
    #     query_args = {'library_uuid': library_uuid}
    #
    #     response = RequestManager.create_request('GET', '/auth/calibre', query_args=query_args)
    #     self.logger.debug(response)
    #     return response

    def status(self, library_uuid, library_name):
        '''
        This function will retrieve the current QuietThyme status and verify that the user can
        authenticate.
        :param library_uuid: calibre library identifier
        :return: quietthyme status object
        '''
        self.logger.debug(sys._getframe().f_code.co_name)

        response = RequestManager.create_request('GET', '/storage/status', query_args={'source': 'calibre'})
        self.logger.debug(response)
        return response

    def create_book(self, local_metadata):
        '''
        This function will find or create a book in QuietThyme with the Calibre metadata provided
        :param local_metadata: calibre metadata
        :return: quietthyme metadata for the book created/found
        '''
        self.logger.debug(sys._getframe().f_code.co_name)

        #create QT book model.
        qt_metadata = {
            'title': local_metadata.title,
            'calibre_id': local_metadata.uuid,
            'average_rating': local_metadata.rating,
            'short_summary': local_metadata.comments,
            'publisher': local_metadata.publisher,
            'published_date': local_metadata.pubdate.utcnow().isoformat("T") + "Z",
            'tags': local_metadata.tags,
            'authors': local_metadata.authors,
            'last_modified': local_metadata.last_modified.utcnow().isoformat("T") + "Z",

            #additional data, not used by qt yet. These field names will change.
            'user_categories': local_metadata.user_categories,
            'user_metadata': local_metadata.get_all_user_metadata(False)
        }
        #set isbn and isbn13 and identifiers
        isbn = local_metadata.identifiers.get('isbn', None)
        if isbn and len(isbn) == 10:
            qt_metadata['isbn10'] = isbn
        elif isbn and len(isbn) == 13:
            qt_metadata['isbn'] = isbn

        amazon_id = local_metadata.identifiers.get('amazon', None)
        if amazon_id:
            qt_metadata['amazon_id'] = amazon_id

        google_id = local_metadata.identifiers.get('google', None)
        if google_id:
            qt_metadata['google_id'] = google_id

        goodreads_id = local_metadata.identifiers.get('goodreads', None)
        if goodreads_id:
            qt_metadata['goodreads_id'] = goodreads_id

        ffiction_id = local_metadata.identifiers.get('ffiction', None)
        if ffiction_id:
            qt_metadata['ffiction_id'] = ffiction_id

        barnesnoble_id = local_metadata.identifiers.get('barnesnoble', None)
        if barnesnoble_id:
            qt_metadata['barnesnoble_id'] = barnesnoble_id

        #series
        if local_metadata.series:
            qt_metadata['series_name'] = local_metadata.series.strip()
            qt_metadata['series_number'] = local_metadata.series_index


        json_data = json.dumps(qt_metadata, sort_keys=True,indent=4, separators=(',', ': '))
        self.logger.debug(json_data)

        response = RequestManager.create_request('POST', '/book', json_data=json_data, query_args={'source': 'calibre'})
        self.logger.debug(response['data']['id'])

        qt_metadata['id'] = response['data']['id']
        return qt_metadata
        # resp = self._make_json_request(QNetworkAccessManager.PostOperation, "/book", json_data=json_data)
        # resp.error.connect(self.handleError)
        # resp.finished.connect(self.handleFinished)
        # self.logger.debug(resp.readAll())

    def books_all(self, storage_id):
        loaded_all = False

        items = []
        page = ""

        while not loaded_all:
            resp = self.books(storage_id, page)
            items = items + resp["data"]["Items"]
            page = resp["data"]["LastEvaluatedKey"]

            if resp["data"]["LastEvaluatedKey"] == "":
                loaded_all = True


        return {
            "data":{
                "Items":items,
                "LastEvaluatedKey": ""
            }
        }



    def books(self, storage_id, page=""):
        '''
        This function will download a list of book metadata from QuietThyme.
        '''

        args = {'storage_id': storage_id}
        if page != "":
            args['page'] = page;
        response = RequestManager.create_request('GET', '/book', query_args=args)
        self.logger.debug(response)
        return response


    def prepare_bookstorage(self, qt_storage_metadata):
        self.logger.debug(sys._getframe().f_code.co_name)

        json_data = json.dumps(qt_storage_metadata, sort_keys=True,indent=4, separators=(',', ': '))
        self.logger.debug(json_data)

        response = RequestManager.create_request('POST', '/storage/prepare/book', json_data=json_data)
        self.logger.debug(response)
        return response


    def prepare_cover_storage(self, qt_book_id, qt_cover_filename, replace_file=False):
        self.logger.debug(sys._getframe().f_code.co_name)

        qt_filename_base, qt_filename_ext = os.path.splitext(qt_cover_filename)
        self.logger.debug(qt_filename_base,qt_filename_ext)


        qt_payload = {
            'book_id': qt_book_id,
            'filename': qt_filename_base,
            'format': qt_filename_ext
        }
        json_data = json.dumps(qt_payload, sort_keys=True,indent=4, separators=(',', ': '))
        self.logger.debug(json_data)

        response = RequestManager.create_request('POST', '/storage/prepare/cover', json_data=json_data)
        self.logger.debug(response)
        return response

    def upload_bookstorage(self, signed_url, local_filepath):
        self.logger.debug(sys._getframe().f_code.co_name)

        # response = RequestManager.create_file_request("/storage/upload/book", {'source':'calibre'},
        #                                           {"book_id": qt_book_id,
        #                                            "storage_id": storage_id,
        #                                            "file_name": qt_filename_base,
        #                                            "format": qt_filename_ext[1:],
        #                                            "replace_file": replace_file
        #                                            },
        #                                           {"file": local_filepath}
        #                                           #{'file':'/home/jason/Documents/Daulton, John/Galactic Mage, The/Galactic Mage, The - John Daulton.mobi'}
        #                                           )
        response = RequestManager.create_signed_file_request(signed_url, local_filepath)

        self.logger.debug(response)
        return response

    def upload_cover(self, signed_url,local_filepath):
        self.logger.debug(sys._getframe().f_code.co_name)

        response = RequestManager.create_signed_file_request(signed_url, local_filepath)

        self.logger.debug(response)
        return response


    def destroy_book(self, calibre_storage_path):
        self.logger.debug(sys._getframe().f_code.co_name)

        import re
        pattern = r"(?P<storage_type>\S+)://(?P<book_id>\S+)/(?P<file_name>\D+)"
        parsed_data = re.search(pattern, calibre_storage_path).groupdict()

        response = RequestManager.create_request('DELETE', '/book/' + parsed_data['book_id'])
        self.logger.debug(response)
        return response

    def download_bookstorage(self, calibre_storage_path):
        self.logger.debug(sys._getframe().f_code.co_name)
        import re
        pattern = r"(?P<storage_type>\S+)://(?P<book_id>\S+)/(?P<file_name>\D+)"
        parsed_data = re.search(pattern, calibre_storage_path).groupdict()

        url_response =  RequestManager.create_request('GET', '/storage/' + parsed_data['book_id'], json_response=True)
        # unfortunaly the API cant do the redirect for us, so we need to start a new request using the url param.
        self.logger.debug(url_response)
        return RequestManager.create_request('GET', url_response['data']['url'], json_response=False, allow_redirects=True, external_request=True)


