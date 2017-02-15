import mimetools
import mimetypes
import io
import codecs
import urllib
import urlparse
import httplib
import socket
import sys
import json
import os
from calibre_plugins.quietthyme.config import prefs
import logging

__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'


class RequestManager(object):
    api_base = prefs['api_base']

    @classmethod
    def create_request(cls, action, endpoint='/', query_args=None, json_data='', json_response=True):
        logger = logging.getLogger(__name__)
        logger.debug(sys._getframe().f_code.co_name)

        if not query_args:
            query_args = {}

        # Build the request
        url = RequestManager.api_base + endpoint
        schema, domain, path, params, query, fragments = \
            urlparse.urlparse(url)

        if query_args:
            encoded_args = urllib.urlencode(query_args)
            path += "?" + encoded_args

        logger.info('Requesting url: %s %s %s' % (schema, domain, path))
        try:

            http = httplib.HTTPSConnection(domain)
            http.connect()
            headers = {}

            if json_data:
                clen = len(json_data)
                headers['Content-Type'] = 'application/json'
                headers['Content-Length'] = clen

            if 'token' in prefs:
                headers['Authorization'] = 'JWT ' + prefs['token']
            http.request(action, path, json_data or None, headers)

            try:
                r = http.getresponse()
                if r.status == 200:
                    logger.debug('Request successful (%s): %s' % (r.status, r.reason))

                    if json_response:
                        data = r.read()
                        logger.debug(data)
                        return json.loads(data)
                    else:
                        return r.read()
                else:
                    logger.error('Request failed (%s): %s' % (r.status, r.reason))
                    logger.error('Response headers: %s' % r.getheaders())
            except Exception, e:
                logger.error(e)
            finally:
                logger.debug('Closing http request')
                http.close()

        except socket.error, e:
            logger.error("Error:", str(e))
            raise SystemExit(1)

    @classmethod
    def create_signed_file_request(self, url, filepath, json_response=False):
        logger = logging.getLogger(__name__)
        logger.debug(sys._getframe().f_code.co_name)

        headers = {
            "Content−type": "application/octet−stream",
            "Accept": "text/plain"
        }

        schema, domain, path, params, query, fragments = \
            urlparse.urlparse(url)

        if query:
            path += "?" + query

        logger.debug("Upload URL: %s" % (path))
        http = httplib.HTTPSConnection(domain)
        http.request("PUT", path, open(filepath, "rb"), headers)


        try:
            r = http.getresponse()
            if r.status == 200:
                logger.debug('Request successful (%s): %s' % (r.status, r.reason))

                if json_response:
                    data = r.read()
                    logger.debug(data)
                    return json.loads(data)
                else:
                    return r.read()
            else:
                logger.error('Request failed (%s): %s' % (r.status, r.reason))
                logger.error('Response headers: %s' % r.getheaders())
                logger.error('Response data: %s' % r.read())
        except Exception, e:
            logger.error(e)
        finally:
            logger.debug('Closing http request')
            http.close()


    #from https://github.com/kovidgoyal/calibre/blob/ef09e886b3d95d6de5c76ad3a179694ae75c65f4/setup/pypi.py#L235
    @classmethod
    def create_file_request(cls, endpoint="/",query_args=None, form_fields=None, filepath_fields=None):
        """

        :param form_fields: simple key value form fields. key=fieldname, value=fieldvalue
        :param filepath_fields: key=fieldname, value=filepath for file that will be uploaded
        :return: response
        """
        logger = logging.getLogger(__name__)
        logger.debug(sys._getframe().f_code.co_name)
        if not query_args:
            query_args = {}
        if not form_fields:
            form_fields = {}
        if not filepath_fields:
            filepath_fields = {}

        form = MultiPartForm()
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
        url = RequestManager.api_base + endpoint
        schema, netloc, url, params, query, fragments = \
            urlparse.urlparse(url)

        if query_args:
            encoded_args = urllib.urlencode(query_args)
            url += "?" + encoded_args

        try:
            form_buffer = form.get_binary().getvalue()
            http = httplib.HTTPConnection(netloc)
            http.connect()
            http.putrequest("POST", url)
            http.putheader('Content-type', form.get_content_type())
            http.putheader('Content-length', str(len(form_buffer)))
            http.putheader('Authorization', "Bearer "+prefs['token'])
            http.endheaders()
            http.send(form_buffer)
        except socket.error, e:
            logger.error("Error:", str(e))
            raise SystemExit(1)

        r = http.getresponse()
        if r.status == 200:
            return json.loads(r.read())
        else:
            logger.error('Upload failed (%s): %s' % (r.status, r.reason))



#from http://pymotw.com/2/urllib2/#uploading-files
class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        self.logger = logging.getLogger(__name__)
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