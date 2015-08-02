__author__ = 'jason'


from PyQt5 import QtCore, QtNetwork
import sys
import time

def finished(reply):
    print "Finished: ", reply.readAll()


def construct_multipart(data, files):
    multiPart = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
    for key, value in data.items():
        textPart = QtNetwork.QHttpPart()
        textPart.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                           "form-data; name=\"%s\"" % key)
        textPart.setBody(value)
        multiPart.append(textPart)

    for key, file in files.items():
        imagePart = QtNetwork.QHttpPart()
        #imagePart.setHeader(QNetworkRequest::ContentTypeHeader, ...);
        fileName = QtCore.QFileInfo(file.fileName()).fileName()
        imagePart.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                            "form-data; name=\"%s\"; filename=\"%s\"" % (key, fileName))
        imagePart.setBodyDevice(file);
        multiPart.append(imagePart)
    return multiPart

file1 = QtCore.QFile('/tmp/1.txt')
file1.open(QtCore.QFile.ReadOnly)
url = QtCore.QUrl('/home/jason/Documents/Daulton, John/Galactic Mage, The/Galactic Mage, The - John Daulton.mobi');
data = { 'text1': 'test1', 'text2': 'test2' }
files = {'file1': file1 }
multipart = construct_multipart(data, files)
request_qt = QtNetwork.QNetworkRequest(url)
request_qt.setRawHeader("Authorization","Bearer x1UQT5N")
request_qt.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader,
                     'multipart/form-data; boundary=%s' % multipart.boundary())
manager = QtNetwork.QNetworkAccessManager()
manager.finished.connect(finished)
request = manager.post(request_qt, multipart)



#
# import codecs,base64, urllib2, os,io
# from cStringIO import StringIO
# import itertools
# import mimetools
# import mimetypes
# import codecs
#
# class MultiPartForm(object):
#     """Accumulate the data to be used when posting a form."""
#
#     def __init__(self):
#         self.form_fields = []
#         self.files = []
#         self.boundary = mimetools.choose_boundary()
#         return
#
#     def get_content_type(self):
#         return 'multipart/form-data; boundary=%s' % self.boundary
#
#     def add_field(self, name, value):
#         """Add a simple field to the form data."""
#         self.form_fields.append((name, value))
#         return
#
#     def add_file(self, fieldname, filename, fileHandle, mimetype=None):
#         """Add a file to be uploaded."""
#         #convert file to base64 file
#         import base64
#         body = base64.b64encode(fileHandle.read())
#         if mimetype is None:
#             mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
#         self.files.append((fieldname, filename, mimetype, body))
#         return
#
#     def __str__(self):
#         """Return a string representing the form data, including attached files."""
#         # Build a list of lists, each containing "lines" of the
#         # request.  Each part is separated by a boundary string.
#         # Once the list is built, return a string where each
#         # line is separated by '\r\n'.
#         parts = []
#         part_boundary = '--' + self.boundary
#
#         # Add the form fields
#         parts.extend(
#             [ part_boundary,
#               'Content-Disposition: form-data; name="%s"' % name,
#               '',
#               value,
#               ]
#             for name, value in self.form_fields
#         )
#
#         # Add the files to upload
#         parts.extend(
#             [ part_boundary,
#               'Content-Disposition: file; name="%s"; filename="%s"' % \
#               (field_name, filename),
#               'Content-Type: %s' % content_type,
#               #'Content-Transfer-Encoding: base64'
#               '',
#               body,
#               ]
#             for field_name, filename, content_type, body in self.files
#         )
#
#         # Flatten the list and add closing boundary marker,
#         # then return CR+LF separated data
#         flattened = list(itertools.chain(*parts))
#         flattened.append('--' + self.boundary + '--')
#         flattened.append('')
#         return '\r\n'.join(flattened)
#
#
#
#
#
# form = MultiPartForm()
# form_fields = {}
# for key, value in form_fields.iteritems():
#     form.add_field(key, str(value))
#
# # Add a fake file
# filepath_fields = {
#     'file': '/home/jason/Documents/Daulton, John/Galactic Mage, The/Galactic Mage, The - John Daulton.mobi',
#     #'file': '/tmp/test.txt'
#    # 'file' : '/home/jason/Documents/Parker, K J/Devices and Desires/Devices and Desires - K J Parker.epub'
# }
# for key, filepath in filepath_fields.iteritems():
#     if os.path.isfile(filepath):
#         form.add_file(key, os.path.basename(filepath),
#                       fileHandle=codecs.open(filepath, "rb"))
#         #fileHandle=StringIO('FILE CONTENTS'))
#     else:
#         raise Exception("The file was not found")
#
# # Build the request
# url = 'http://localhost:1337/storage'
# request = urllib2.Request(url)
# request.add_header("Authorization","Bearer x1UQT5N")
# body = str(form)
# request.add_header('Content-type', form.get_content_type())
# request.add_header('Content-length', len(body))
# request.add_data(body)
#
# try:
#     connection = urllib2.urlopen(request)
# except urllib2.HTTPError,e:
#     connection = e
#
#     # check. Substitute with appropriate HTTP code.
# if connection.code == 200:
#     data = connection.read()
#     print(data)
#
# else:
#     print("Error:", connection.code)
#     raise connection