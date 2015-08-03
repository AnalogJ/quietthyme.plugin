from calibre_plugins.quietthyme.config import prefs
import sys
import io
import json
import mimetools
import mimetypes
import codecs
import os
import urllib
import urllib2
import urlparse
import httplib
import socket

# from PyQt5.Qt import (QNetworkAccessManager,QNetworkReply, QNetworkRequest, QUrl, QByteArray)
# from PyQt5.QtCore import QIODevice, QBuffer, QByteArray

class ApiClient():
    def __init__(self, logger):
        self.api_base = "http://" +  prefs['api_base']
        #self.network_manager = QNetworkAccessManager()
        self.logger = logger

    def auth(self, library_uuid, library_name):
        '''
        This function will authenticate with Quietthyme and generate a JWT for subsequent api calls.
        :param library_uuid: calibre library identifier
        :return: quietthyme jwt.
        '''
        self.logger.debug(sys._getframe().f_code.co_name)
        query_args = {'library_uuid': library_uuid,
                      'library_name': library_name}

        response = self._make_json_request('GET', '/api/auth/calibre', query_args=query_args)
        self.logger.debug(response)
        return response

    def status(self, library_uuid, library_name):
        '''
        This function will retrieve the current QuietThyme status and verify that the user can
        authenticate.
        :param library_uuid: calibre library identifier
        :return: quietthyme status object
        '''
        self.logger.debug(sys._getframe().f_code.co_name)

        response = self._make_json_request('GET', '/api/storage/status')
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
            'authors': [{'name': author} for author in local_metadata.authors],
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

        response = self._make_json_request('POST', '/book', json_data=json_data, query_args={'source': 'calibre'})
        self.logger.debug(response['id'])

        qt_metadata['id'] = response['id']
        return qt_metadata
        # resp = self._make_json_request(QNetworkAccessManager.PostOperation, "/book", json_data=json_data)
        # resp.error.connect(self.handleError)
        # resp.finished.connect(self.handleFinished)
        # self.logger.debug(resp.readAll())

    def set_book_cover(self, qt_book_id, cover_local_filepath):
        self.logger.debug(sys._getframe().f_code.co_name)
        response = self._make_upload_file_request("/book_cover",
                                                  {"book_id": qt_book_id},
                                                  {"file": cover_local_filepath}
                                                  #{'file':'/home/jason/Documents/Daulton, John/Galactic Mage, The/Galactic Mage, The - John Daulton.mobi'}
        )
        self.logger.debug(response)
        return response

    def books(self, storage_type):
        '''
        This function will download a list of book metadata from QuietThyme.
        '''

        response = self._make_json_request('GET', '/book', query_args={'storage_type': storage_type})
        self.logger.debug(response)
        return response


    def create_bookstorage(self, qt_book_id, storage_type, local_filepath, qt_filename, replace_file=False):
        self.logger.debug(sys._getframe().f_code.co_name)

        qt_filename_base, qt_filename_ext = os.path.splitext(qt_filename)
        self.logger.debug(qt_filename_base,qt_filename_ext)
        response = self._make_upload_file_request("/storage",
                                                  {"book_id": qt_book_id,
                                                   "storage_type": storage_type,
                                                   "file_name": qt_filename_base,
                                                   "format": qt_filename_ext[1:],
                                                   "replace_file": replace_file
                                                  },
                                                  {"file": local_filepath}
                                                #{'file':'/home/jason/Documents/Daulton, John/Galactic Mage, The/Galactic Mage, The - John Daulton.mobi'}
        )
        self.logger.debug(response)
        return response

    def destroy_bookstorage(self, calibre_storage_path):
        self.logger.debug(sys._getframe().f_code.co_name)

        import re
        pattern = r"(?P<storage_type>\S+)://(?P<bookstorage_id>\S+)/(?P<file_name>\D+)"
        parsed_data = re.search(pattern, calibre_storage_path).groupdict()

        response = self._make_json_request('DELETE', '/storage/' + parsed_data['bookstorage_id'])
        self.logger.debug(response)
        return response

    def download_bookstorage(self, calibre_storage_path):
        self.logger.debug(sys._getframe().f_code.co_name)
        import re
        pattern = r"(?P<storage_type>\S+)://(?P<bookstorage_id>\S+)/(?P<file_name>\D+)"
        parsed_data = re.search(pattern, calibre_storage_path).groupdict()

        return self._make_json_request('GET', '/storage/' + parsed_data['bookstorage_id'] + '/download', json_response=False)

    def _make_json_request(self, action, endpoint='/', query_args={}, json_data='', json_response=True):
        self.logger.debug(sys._getframe().f_code.co_name)
        # Build the request
        url = self.api_base + endpoint
        schema, domain, path, params, query, fragments = \
            urlparse.urlparse(url)

        if query_args:
            encoded_args = urllib.urlencode(query_args)
            path += "?" + encoded_args

        self.logger.debug(domain, path)
        try:

            http = httplib.HTTPConnection(domain)
            http.connect()
            headers = {}

            if json_data:
                clen = len(json_data)
                headers['Content-Type'] = 'application/json'
                headers['Content-Length'] = clen

            if 'token' in prefs:
                headers['Authorization'] = 'Bearer ' + prefs['token']

            self.logger.debug('before request')
            http.request(action, path, json_data or None, headers)

            try:
                self.logger.debug('before response')
                r = http.getresponse()
                self.logger.debug('after response')

                if r.status == 200:
                    self.logger.debug('Request successful (%s): %s' % (r.status, r.reason))

                    if json_response:
                        data = r.read()
                        self.logger.debug(data)
                        return json.loads(data)
                    else:
                        return r.read()
                else:
                    self.logger.debug('Request failed (%s): %s' % (r.status, r.reason))
            except Exception, e:
                self.logger.debug(e)
            finally:
                self.logger.debug('Closing http request')

                http.close()

        except socket.error, e:
            self.logger.debug("Error:", str(e))
            raise SystemExit(1)


    #from https://github.com/kovidgoyal/calibre/blob/ef09e886b3d95d6de5c76ad3a179694ae75c65f4/setup/pypi.py#L235
    def _make_upload_file_request(self, endpoint="/", form_fields={}, filepath_fields={}):
        """

        :param form_fields: simple key value form fields. key=fieldname, value=fieldvalue
        :param filepath_fields: key=fieldname, value=filepath for file that will be uploaded
        :return: response
        """
        form = MultiPartForm(self.logger)
        for key, value in form_fields.iteritems():
            form.add_field(key, str(value))

        # Add a fake file
        for key, filepath in filepath_fields.iteritems():
            if os.path.isfile(filepath):
                form.add_file(key, os.path.basename(filepath),
                      fileHandle=codecs.open(filepath, "rb"))
                     #fileHandle=StringIO('FILE CONTENTS'))
            else:
                raise Exception("The file was not found")

        # Build the request
        url = self.api_base + endpoint
        schema, netloc, url, params, query, fragments = \
            urlparse.urlparse(url)

        try:
            form_buffer =  form.get_binary().getvalue()
            http = httplib.HTTPConnection(netloc)
            http.connect()
            http.putrequest("POST", url)
            http.putheader('Content-type', form.get_content_type())
            http.putheader('Content-length', str(len(form_buffer)))
            http.putheader('Authorization', "Bearer "+prefs['token'])
            http.endheaders()
            http.send(form_buffer)
        except socket.error, e:
            self.logger.debug("Error:", str(e))
            raise SystemExit(1)

        r = http.getresponse()
        if r.status == 200:
            return json.loads(r.read())
        else:
            self.logger.debug('Upload failed (%s): %s' % (r.status, r.reason))


#from http://pymotw.com/2/urllib2/#uploading-files
class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self, logger):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        self.logger = logger
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        #convert file to base64 file
        import base64
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def get_binary(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        part_boundary = '--' + self.boundary

        binary = io.BytesIO()
        needsCLRF = False
        # Add the form fields
        for name, value in self.form_fields:
            if needsCLRF:
                self.logger.debug('\r\n')
                binary.write('\r\n')
            needsCLRF = True

            block = [part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value
            ]
            self.logger.debug('\r\n'.join(block))
            binary.write('\r\n'.join(block))

        # Add the files to upload
        for field_name, filename, content_type, body in self.files:
            if needsCLRF:
                self.logger.debug('\r\n')
                binary.write('\r\n')
            needsCLRF = True

            block = [part_boundary,
              str('Content-Disposition: file; name="%s"; filename="%s"' % \
              (field_name, filename)),
              'Content-Type: %s' % content_type,
              #'Content-Transfer-Encoding: base64'
              ''
              ]
            self.logger.debug('\r\n'.join(block))
            self.logger.debug('\r\n')
            self.logger.debug('BODY OF FILE GOES HERE')
            binary.write('\r\n'.join(block))
            binary.write('\r\n')
            binary.write(body)


        # add closing boundary marker,
        self.logger.debug('\r\n--' + self.boundary + '--\r\n')
        binary.write('\r\n--' + self.boundary + '--\r\n')
        return binary