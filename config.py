#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QVBoxLayout, QWebView,QWebPage, QWebSecurityOrigin,QWebInspector, QSsl, QUrl, QSize, \
    QNetworkAccessManager, QWebSettings, QNetworkReply, QNetworkRequest,QWebFrame,QByteArray, QSslConfiguration, \
    QSslSocket, QSslCertificate, QCheckBox, QSizePolicy

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/quietthyme) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/quietthyme')

# Set defaults
# determines if the plugin logger is enabled.
prefs.defaults['debug_mode'] = False
# determines if the plugin communicates with build.quietthyme.com or www.quietthyme.com
# TODO: this should be build.quiethyme.com or www.quietthyme.com when ready
#prefs.defaults['api_base'] = 'localhost:1337'
prefs.defaults['api_base'] = 'build.quietthyme.com'
# (String) the access token used to communicate with the quietthyme API
# TODO: this should be None when deployed.
prefs.defaults['token'] = ''

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        #add checkbox
        self.debug_checkbox = QCheckBox('Debug Mode')
        self.debug_checkbox.setChecked(prefs['debug_mode'])
        self.l.addWidget(self.debug_checkbox)

        self.config_url = QUrl('https://'+prefs['api_base']+'/link/start')
        self.webview = QTWebView(bearer_token=prefs['token'])

        self.webview.load(self.config_url)
        if prefs['debug_mode']:
            self.webview.setMinimumSize(QSize(600, 300))
        else:
            self.webview.setMinimumSize(QSize(600, 600))
        self.global_settings = self.webview.page().settings() #QWebSettings.globalSettings()
        self.global_settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.global_settings.setAttribute(QWebSettings.JavascriptEnabled, True)
        self.global_settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.global_settings.setAttribute(QWebSettings.JavascriptCanCloseWindows, True)
        self.global_settings.setAttribute(QWebSettings.PluginsEnabled, True)
        self.global_settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        self.global_settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.global_settings.setAttribute(QWebSettings.XSSAuditingEnabled, False)
        self.global_settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, True)
        self.webview.show()
        self.l.addWidget(self.webview)

        if prefs['debug_mode']:
            self.inspector = QWebInspector()
            self.inspector.setMinimumSize(QSize(600, 300))
            self.inspector.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);

            self.l.addWidget(self.inspector)
            self.inspector.setPage(self.webview.page())

        # self.webview.urlChanged.connect(_url_changed)
        # self.webview.loadFinished.connect(_load_finished)

    ################################################################################################################
    # Event Handlers
    #
    # def _url_changed(url):
    #         print('url changed: ', url)
    #
    # def _load_finished(ok):
    #     print('load finished, ok: ', ok)
    #     if self.webview.page().mainFrame().url() == self.config_url:
    #         print('requested url = current url')
    #         # token = self.webview.page().mainFrame().evaluateJavaScript("""
    #         # getAuthToken();
    #         # """)
    #         # print(token)
    #         # prefs['token'] = token

    def save_settings(self):
        prefs['debug_mode'] = self.debug_checkbox.isChecked()

    def validate(self):
        return True #self.webview.page().mainFrame().url() == self.config_url

class QTWebView(QWebView):

    def __init__(self, parent=None, bearer_token=None):
        super(QWebView,self).__init__(parent)
        page = QTWebPage(bearer_token=bearer_token)
        self.setPage(page)
        #TODO: if token is invalid, show a landing page.


class QTWebPage(QWebPage):
    """ Settings for the browser."""

    def __init__(self, parent=None, bearer_token=None):
        super(QWebPage, self).__init__(parent)
        self.bearer_token = bearer_token
        self.nam = QTNetworkManager(bearer_token=bearer_token)
        self.setNetworkAccessManager(self.nam)
    # def userAgentForUrl(self, url):
    #     """ Returns a User Agent that will be seen by the website. """
    #     return "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"

    def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
        if prefs['debug_mode']:
            print("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))

    def acceptNavigationRequest(self, frame, request, type):
        print("NavReq: %s: %s " % (request.url(), type))

        origin = frame.securityOrigin()
        print("Setting new Security Origin: %s " % origin.host())

        self.nam = QTNetworkManager(bearer_token=self.bearer_token,frame_origin=origin)
        self.setNetworkAccessManager(self.nam)
        return True



class QTNetworkManager(QNetworkAccessManager):

    def __init__(self, bearer_token=None, frame_origin=None):
        super(QNetworkAccessManager,self).__init__()
        self.bearer_token = bearer_token
        self.sslErrors.connect(self._ssl_errors)
        self.frame_origin = frame_origin

    def createRequest(self, operation, request, data):
        request_host = request.url().host()
        request_path = request.url().path()
        quietthyme_host = QUrl('http://' + prefs['api_base']).host()

        if self.bearer_token and (quietthyme_host == request_host): #and not(request_path.startswith('/link/callback')):
            print("Adding QT Auth header: %s", request.url())
            request.setRawHeader("Authorization", "Bearer %s" % self.bearer_token)

        if quietthyme_host == request_host:
            #TODO Huge hack. only because QT5 cant seeem to consistently communicate over SSL when using sni. ie cloudflare.
            url = request.url()
            url.setScheme('http')
            request.setUrl(url)

        if self.frame_origin:
            #adding the current resource request to the security origin witelist.
            self.frame_origin.addAccessWhitelistEntry("http", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("https", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("qrc", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("data", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("https", request.url().host(), QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("http", request.url().host(), QWebSecurityOrigin.AllowSubdomains)

        print("Requesting: %s" % request.url())
        reply = QNetworkAccessManager.createRequest(self,operation, request, data)
        return reply
    #     #if operation == self.GetOperation or operation == self.HeadOperation or operation == self.CustomOperation:
    #     reply = QTNetworkReply(self, reply,operation)
    #
    #     # add Base-Url header, then we can get it from QWebView
    #     # WTF?
    #     if isinstance(request.originatingObject(), QWebFrame):
    #         try:
    #             reply.setRawHeader(QByteArray('Base-Url'), QByteArray('').append(request.originatingObject().page().mainFrame().baseUrl().toString()))
    #             # reply.setRawHeader("Content-Security-Policy", "default-src '*'; style-src '*' 'unsafe-inline'; script-src '*' 'unsafe-inline' 'unsafe-eval'")
    #             # reply.setRawHeader("Access-Control-Allow-Origin", "*")
    #             # reply.setRawHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    #         except Exception as e:
    #             print(e)
    #
    #
    #     return reply

    ################################################################################################################
    # Event Handlers
    def _ssl_errors(self,reply, errors):
        print ("SSL error occured while requesting: %s . Will try to ignore" % reply.url())
        reply.ignoreSslErrors()

# class QTNetworkReply(QNetworkReply):
#
#     """
#     Credits:
#     * https://code.google.com/p/webscraping/source/browse/webkit.py#154
#     * http://gitorious.org/qtwebkit/performance/blobs/master/host-tools/mirror/main.cpp
#     """
#     def __init__(self, parent, original_reply, operation):
#         super(QNetworkReply,self).__init__(parent)
#
#         self.original_reply = original_reply # reply to proxy
#         self.operation = operation
#         self.data = '' # contains downloaded data
#         self.buffer = '' # contains buffer of data to read
#         self.setOpenMode(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)
#
#         # connect signal from proxy reply
#         self.original_reply.metaDataChanged.connect(self.applyMetaData)
#         self.original_reply.readyRead.connect(self.readInternal)
#         self.original_reply.error.connect(self.error)
#         self.original_reply.finished.connect(self.finished)
#         self.original_reply.uploadProgress.connect(self.uploadProgress)
#         self.original_reply.downloadProgress.connect(self.downloadProgress)
#         self.original_reply.sslErrors.connect(self.sslErrors)
#
#
#     def sslErrors(self,errors):
#         print('===========QT REPLY ERRORS')
#         for error in errors:
#             print(error.errorString())
#         self.ignoreSslErrors()
#
#     def __getattribute__(self, attr):
#         """Send undefined methods straight through to proxied reply
#         """
#         # send these attributes through to proxy reply
#         if attr in ('operation', 'request', 'url', 'abort', 'close'):#, 'isSequential'):
#             value = self.original_reply.__getattribute__(attr)
#         else:
#             value = QNetworkReply.__getattribute__(self, attr)
#         #print attr, value
#         return value
#
#     def abort(self):
#         pass # qt requires that this be defined
#
#     def isSequential(self):
#         return True
#
#     def applyMetaData(self):
#         for header in self.original_reply.rawHeaderList():
#             #print('RAW HEADER: %s =>  %s' % (header, self.original_reply.rawHeader(header)))
#             self.setRawHeader(header, self.original_reply.rawHeader(header))
#
#         headers = (
#             QNetworkRequest.ContentTypeHeader,
#             QNetworkRequest.ContentLengthHeader,
#             QNetworkRequest.LocationHeader,
#             QNetworkRequest.LastModifiedHeader,
#             QNetworkRequest.SetCookieHeader,
#         )
#         for header in headers:
#             self.setHeader(header, self.original_reply.header(header))
#
#         attributes = (
#             QNetworkRequest.HttpStatusCodeAttribute,
#             QNetworkRequest.HttpReasonPhraseAttribute,
#             QNetworkRequest.RedirectionTargetAttribute,
#             QNetworkRequest.ConnectionEncryptedAttribute,
#             QNetworkRequest.CacheLoadControlAttribute,
#             QNetworkRequest.CacheSaveControlAttribute,
#             QNetworkRequest.SourceIsFromCacheAttribute,
#
#         )
#         for attr in attributes:
#             self.setAttribute(attr, self.original_reply.attribute(attr))
#
#         # make sure the content-security-policy header is open (otherwise we run into blankscreen/javasccritp issues)
#         self.setRawHeader("Content-Security-Policy", "default-src '*'; style-src '*' 'unsafe-inline'; script-src '*' 'unsafe-inline' 'unsafe-eval'")
#         #self.setRawHeader("Access-Control-Allow-Origin", "*")
#         #self.setRawHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#         self.metaDataChanged.emit()
#
#     def bytesAvailable(self):
#         """
#         How many bytes in the buffer are available to be read
#         """
#
#         return len(self.buffer) + QNetworkReply.bytesAvailable(self)
#
#     def readInternal(self):
#         """
#         New data available to read
#         """
#
#         s = self.original_reply.readAll()
#         self.data += s
#         self.buffer += s
#         self.readyRead.emit()
#
#     def readData(self, size):
#         """Return up to size bytes from buffer
#         """
#         size = min(size, len(self.buffer))
#         data, self.buffer = self.buffer[:size], self.buffer[size:]
#         return str(data)
#
