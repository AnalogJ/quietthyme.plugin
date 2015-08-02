#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'
from PyQt5.Qt import QWidget, QHBoxLayout, QWebView, QUrl, QSize, QNetworkAccessManager
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

        self.config_url = QUrl('http://'+prefs['api_base']+'/calibre/config')

        # self.label = QLabel(' Hello world4 &message:')
        # self.l.addWidget(self.label)
        #
        # self.msg = QLineEdit(self)
        # self.msg.setText(prefs['hello_world_msg'])
        # self.l.addWidget(self.msg)
        # self.label.setBuddy(self.msg)


        self.webview = QTWebView(bearer_token=prefs['access_token'])

        #setup events for the webview.
        def url_changed(url):
            print('url changed: ', url)

        def load_finished(ok):
            print('load finished, ok: ', ok)
            if self.webview.page().mainFrame().url() == self.config_url:
                print('requested url = current url')
                token = self.webview.page().mainFrame().evaluateJavaScript("""
                getAuthToken();
                """)
                print(token)
                prefs['access_token'] = token


        self.webview.loadFinished.connect(load_finished)
        self.webview.urlChanged.connect(url_changed)
        # self.webview.connect(self.webview, SIGNAL("linkClicked(const QUrl&)"), link_clicked)
        # self.webview.connect(self.webview, SIGNAL('loadStarted()'), load_started)
        # self.webview.connect(self.webview, SIGNAL('loadFinished(bool)'), load_finished)

        self.webview.load(self.config_url)
        self.webview.setMinimumSize(QSize(600, 600))
        self.webview.show()
        self.l.addWidget(self.webview)

        # self.checkbox_beta = QCheckBox("Enable Beta Mode")
        # self.l.addWidget(self.checkbox_beta)


    def save_settings(self):
        prefs['test'] = unicode('test') #unicode(self.msg.text())

    def validate(self):
        return self.webview.page().mainFrame().url() == self.config_url

class QTWebView(QWebView):

    def __init__(self, parent=None, bearer_token=None):
        super(QWebView,self).__init__(parent)
        self.nam = QTNetworkManager(bearer_token)
        self.page().setNetworkAccessManager(self.nam)


class QTNetworkManager(QNetworkAccessManager):

    def __init__(self, bearer_token=None):
        super(QNetworkAccessManager,self).__init__()
        self.bearer_token = bearer_token

    def createRequest(self, operation, request, data):
        if self.bearer_token:
            request.setRawHeader("Authorization", "Bearer %s" % self.bearer_token)

        return QNetworkAccessManager.createRequest(self,operation, request, data)
