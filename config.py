#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'
from PyQt5.Qt import QWidget, QHBoxLayout, QWebView,QWebPage, QWebSecurityOrigin, QUrl, QSize, QNetworkAccessManager, QWebSettings, QNetworkReply, QNetworkRequest,QWebFrame,QByteArray
from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/quietthyme) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/quietthyme')

# Set defaults
# determines if the plugin logger is enabled.
prefs.defaults['debug_plugin'] = True
# determines if the plugin communicates with build.quietthyme.com or www.quietthyme.com
# TODO: this should be build.quiethyme.com or www.quietthyme.com when ready
#prefs.defaults['api_base'] = 'localhost:1337'
prefs.defaults['api_base'] = 'build.quietthyme.com'
#prefs.defaults['api_base'] = 'http://192.150.23.196:1337/'
# (String) the access token used to communicate with the quietthyme API
# TODO: this should be None when deployed.
prefs.defaults['access_token'] = ''
# (String) the UTC expiry date for the access token, None means it never expires. (Will be validated on server side)
prefs.defaults['access_token_expires'] = None


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        #self.config_url = QUrl.fromEncoded('http://'+prefs['api_base']+'/link/start')

        self.config_url = QUrl.fromEncoded('https://www.dropbox.com/login')
        #self.config_url = QUrl.fromEncoded('https://accounts.google.com/ServiceLogin#identifier')
        #self.config_url = QUrl.fromEncoded('http://www.google.com')
        # self.label = QLabel(' Hello world4 &message:')
        # self.l.addWidget(self.label)
        #
        # self.msg = QLineEdit(self)
        # self.msg.setText(prefs['hello_world_msg'])
        # self.l.addWidget(self.msg)
        # self.label.setBuddy(self.msg)


        self.webview = QTWebView(bearer_token=prefs['token'])
        #self.webview.setPage(WebPage())
        #setup events for the webview.
        def url_changed(url):
            print('url changed: ', url)
        #
        # def load_finished(ok):
        #     print('load finished, ok: ', ok)
        #     if self.webview.page().mainFrame().url() == self.config_url:
        #         print('requested url = current url')
        #         # token = self.webview.page().mainFrame().evaluateJavaScript("""
        #         # getAuthToken();
        #         # """)
        #         # print(token)
        #         # prefs['token'] = token
        #
        #
        # self.webview.loadFinished.connect(load_finished)
        self.webview.urlChanged.connect(url_changed)

        self.webview.load(self.config_url)
        self.webview.setMinimumSize(QSize(600, 600))
        self.global_settings = QWebSettings.globalSettings()
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

        # for scheme in ['http','https','data']:
        #     QWebSecurityOrigin.addLocalScheme(scheme)
        #

        # self.checkbox_beta = QCheckBox("Enable Beta Mode")
        # self.l.addWidget(self.checkbox_beta)


    def save_settings(self):
        prefs['test'] = unicode('test') #unicode(self.msg.text())

    def validate(self):
        return self.webview.page().mainFrame().url() == self.config_url

class QTWebPage(QWebPage):
    """ Settings for the browser."""

    def __init__(self, logger=None, parent=None):
        super(QWebPage, self).__init__(parent)
        # self.loadProgress.connect(self._load_started)
    # #     self.setForwardUnsupportedContent(True)
    # #     self.unsupportedContent.connect(self.unsupported)
    # #
    # # def unsupported(self, reply):
    # #     print("=========UNSUPPORTED CONTENT")
    # #
    # # def userAgentForUrl(self, url):
    # #     """ Returns a User Agent that will be seen by the website. """
    # #     return "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"
    #
    # def _load_started(self,status):
    #     print('========WEBFRAME URL: %s SECURITY URL: %s' % (self.mainFrame().url(),self.mainFrame().securityOrigin().host()))
    #     self.mainFrame().securityOrigin().addAccessWhitelistEntry('https','dropboxstatic.com',QWebSecurityOrigin.AllowSubdomains)
    #     self.mainFrame().securityOrigin().addAccessWhitelistEntry('https','dropbox.com',QWebSecurityOrigin.AllowSubdomains)
    #     self.mainFrame().securityOrigin().addAccessWhitelistEntry('https','googleapis.com',QWebSecurityOrigin.AllowSubdomains)

    def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
        print("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))

    def javaScriptAlert(self,originatingFrame,  msg):
        print("JsAlert: %s" % (msg))

    def javaScriptConfirm(self,originatingFrame, msg):
        print("JsAlert: %s" % (msg))
        return True

    def javaScriptPrompt(self, frame, msg, defaultValue, result):
        print("JsPrompt: %s: %s" % (msg,defaultValue))
        return True

    def acceptNavigationRequest(self, frame, request, type):
        print("NavReq: %s: %s" % (request.url(),type))


        #origin = QWebSecurityOrigin(request.url())
        origin = frame.securityOrigin()
        print("URL_CHANGED %s" % origin.host())
        origin.addAccessWhitelistEntry("http", "", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("https", "", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("qrc", "", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("data", "", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("http", "www.youtube.com", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("https", "fonts.googleapis.com", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("https", "cf.dropboxstatic.com", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("https", "fonts.gstatic.com", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry("https", "ajax.googleapis.com", QWebSecurityOrigin.AllowSubdomains)
        origin.addAccessWhitelistEntry(request.url().scheme(), request.url().host(), QWebSecurityOrigin.AllowSubdomains)
        #frame.securityOrigin().allOrigins().append(origin)

        return True

class QTWebView(QWebView):

    def __init__(self, parent=None, bearer_token=None):
        super(QWebView,self).__init__(parent)
        self.setPage(QTWebPage())
        self.nam = QTNetworkManager(bearer_token)
        self.page().setNetworkAccessManager(self.nam)

        self.urlChanged.connect(self._url_changed)
    #
    # def _result_available(self, ok):
    #     print("Result availale")
    #     frame = self.page().mainFrame()
    #     print(frame.toHtml().encode('utf-8'))

    def _url_changed(self, url):
        origin = self.page().mainFrame().securityOrigin()
        #print("URL_CHANGED %s" % origin.host())

        # origin.addAccessWhitelistEntry("http", "", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("https", "", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("qrc", "", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("data", "", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("http", "www.youtube.com", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("https", "fonts.googleapis.com", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("https", "cf.dropboxstatic.com", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("https", "fonts.gstatic.com", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry("https", "ajax.googleapis.com", QWebSecurityOrigin.AllowSubdomains)
        # origin.addAccessWhitelistEntry(url.scheme(), url.host(), QWebSecurityOrigin.AllowSubdomains)






class QTNetworkManager(QNetworkAccessManager):

    def __init__(self, bearer_token=None):
        super(QNetworkAccessManager,self).__init__()
        self.bearer_token = bearer_token


    # def createRequest(self, operation, request, data):
    #     request_host = request.url().host()
    #     quietthyme_host = QUrl.fromEncoded('http://' + prefs['api_base']).host()
    #
    #     if self.bearer_token and (quietthyme_host == request_host):
    #         print("Adding QT Auth header: %s", request.url())
    #         request.setRawHeader("Authorization", "Bearer %s" % self.bearer_token)
    #
    #
    #     reply = QNetworkAccessManager.createRequest(self,operation, request, data)
    #
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

class QTNetworkReply(QNetworkReply):

    """
    Credits:
    * https://code.google.com/p/webscraping/source/browse/webkit.py#154
    * http://gitorious.org/qtwebkit/performance/blobs/master/host-tools/mirror/main.cpp
    """
    def __init__(self, parent, original_reply, operation):
        super(QNetworkReply,self).__init__(parent)

        self.original_reply = original_reply # reply to proxy
        self.operation = operation
        self.data = '' # contains downloaded data
        self.buffer = '' # contains buffer of data to read
        self.setOpenMode(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)

        # connect signal from proxy reply
        self.original_reply.metaDataChanged.connect(self.applyMetaData)
        self.original_reply.readyRead.connect(self.readInternal)
        self.original_reply.error.connect(self.error)
        self.original_reply.finished.connect(self.finished)
        self.original_reply.uploadProgress.connect(self.uploadProgress)
        self.original_reply.downloadProgress.connect(self.downloadProgress)


        print('====ORGINAL OPERATION: %s - %s' % (operation, original_reply.url()))

    def __getattribute__(self, attr):
        """Send undefined methods straight through to proxied reply
        """
        # send these attributes through to proxy reply
        if attr in ('operation', 'request', 'url', 'abort', 'close'):#, 'isSequential'):
            value = self.original_reply.__getattribute__(attr)
        else:
            value = QNetworkReply.__getattribute__(self, attr)
        #print attr, value
        return value

    def abort(self):
        pass # qt requires that this be defined

    def isSequential(self):
        return True

    def applyMetaData(self):
        for header in self.original_reply.rawHeaderList():
            #print('RAW HEADER: %s =>  %s' % (header, self.original_reply.rawHeader(header)))
            self.setRawHeader(header, self.original_reply.rawHeader(header))

        headers = (
            QNetworkRequest.ContentTypeHeader,
            QNetworkRequest.ContentLengthHeader,
            QNetworkRequest.LocationHeader,
            QNetworkRequest.LastModifiedHeader,
            QNetworkRequest.SetCookieHeader,
        )
        for header in headers:
            self.setHeader(header, self.original_reply.header(header))

        attributes = (
            QNetworkRequest.HttpStatusCodeAttribute,
            QNetworkRequest.HttpReasonPhraseAttribute,
            QNetworkRequest.RedirectionTargetAttribute,
            QNetworkRequest.ConnectionEncryptedAttribute,
            QNetworkRequest.CacheLoadControlAttribute,
            QNetworkRequest.CacheSaveControlAttribute,
            QNetworkRequest.SourceIsFromCacheAttribute,

        )
        for attr in attributes:
            self.setAttribute(attr, self.original_reply.attribute(attr))

        # make sure the content-security-policy header is open (otherwise we run into blankscreen/javasccritp issues)
        self.setRawHeader("Content-Security-Policy", "default-src '*'; style-src '*' 'unsafe-inline'; script-src '*' 'unsafe-inline' 'unsafe-eval'")
        #self.setRawHeader("Access-Control-Allow-Origin", "*")
        #self.setRawHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.metaDataChanged.emit()

    def bytesAvailable(self):
        """
        How many bytes in the buffer are available to be read
        """

        return len(self.buffer) + QNetworkReply.bytesAvailable(self)

    def readInternal(self):
        """
        New data available to read
        """

        s = self.original_reply.readAll()
        self.data += s
        self.buffer += s
        self.readyRead.emit()

    def readData(self, size):
        """Return up to size bytes from buffer
        """
        size = min(size, len(self.buffer))
        data, self.buffer = self.buffer[:size], self.buffer[size:]
        return str(data)

