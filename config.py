#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QVBoxLayout, QWebView,QWebPage, QWebSecurityOrigin,QWebInspector, QSsl, QUrl, QSize, \
    QNetworkAccessManager, QWebSettings, QNetworkReply, QNetworkRequest,QWebFrame,QByteArray, QSslConfiguration, QSslError, \
    QSslSocket, QSslCertificate, QCheckBox, QSizePolicy, QStandardPaths, QMessageBox, QTemporaryDir, QRegExp

from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR
import ssl

import logging, sys
from calibre.utils.config import JSONConfig
logger = logging.getLogger(__name__)
# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/quietthyme) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/quietthyme')

# Set defaults
# determines if the web inspector panel is enabled is enabled.
prefs.defaults['inspector_enabled'] = False

prefs.defaults['log_level'] = 'INFO'

# determines if the plugin communicates with beta or master
prefs.defaults['beta_mode'] = False

# (String) the access token used to communicate with the quietthyme API
prefs.defaults['token'] = ''

master_api_base = 'https://api.quietthyme.com/v1'
master_web_base = 'https://www.quietthyme.com'

beta_api_base = 'https://api.quietthyme.com/beta'
beta_web_base = 'https://beta.quietthyme.com'

# default endpoint information should point to Production service.
prefs.defaults['api_base'] = 'https://api.quietthyme.com/v1'
prefs.defaults['web_base'] = 'https://www.quietthyme.com'


if prefs['beta_mode']:
    prefs['api_base'] = beta_api_base
    prefs['web_base'] = beta_web_base
else:
    prefs['api_base'] = master_api_base
    prefs['web_base'] = master_web_base



class ConfigWidget(QWidget):

    def __init__(self):
        self.plugin_prefs = prefs
        self.restart_required = False
        self.inspector = None

        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        #add checkbox
        self.inspector_checkbox = QCheckBox('Show Inspector')
        self.inspector_checkbox.setChecked(self.plugin_prefs.get('inspector_enabled', False))
        self.inspector_checkbox.stateChanged.connect(self._inspector_enabled_changed)
        self.inspector_checkbox.setToolTip('Enable Javascript Console for debugging WebView requests to QuietThyme API')
        self.l.addWidget(self.inspector_checkbox)

        self.beta_checkbox = QCheckBox('Beta Mode')
        self.beta_checkbox.setChecked(self.plugin_prefs.get('beta_mode', False))
        self.beta_checkbox.stateChanged.connect(self._set_restart_required)
        self.beta_checkbox.stateChanged.connect(self._beta_mode_changed)
        self.beta_checkbox.setToolTip('Tell Calibre to communicate with the Beta version of QuietThyme')
        self.l.addWidget(self.beta_checkbox)

        self.config_url = QUrl(self.plugin_prefs.get('web_base')+'/storage')
        self.webview = QTWebView(bearer_token=self.plugin_prefs.get('token'))

        self.webview.load(self.config_url)
        self.global_settings = self.webview.page().settings() #QWebSettings.globalSettings()

        self.global_settings.setAttribute(QWebSettings.LocalStorageEnabled, True) #required since this is where we store tokens.
        self.global_settings.setAttribute(QWebSettings.PrivateBrowsingEnabled,False)
        self.global_settings.setAttribute(QWebSettings.JavascriptEnabled, True)
        self.global_settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.global_settings.setAttribute(QWebSettings.JavascriptCanCloseWindows, True)
        self.global_settings.setAttribute(QWebSettings.PluginsEnabled, True)
        self.global_settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        self.global_settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.global_settings.setAttribute(QWebSettings.XSSAuditingEnabled, False)
        self.global_settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)


        # ensure that we get a random offline/localstorage/cache path for the brower (so that the localstorage data is not persistent across sessions)
        path = None
        while True:
            potential_path = QTemporaryDir()
            if potential_path.isValid():
                path = potential_path.path()
                break

        self.global_settings.setOfflineStoragePath(path)
        self.global_settings.setOfflineWebApplicationCachePath(path)
        self.global_settings.enablePersistentStorage(path)
        self.global_settings.setLocalStoragePath(path)

        self.webview.show()
        self.l.addWidget(self.webview)

        self.configure_webview_inspector_ui()

        self.webview.urlChanged.connect(self._url_changed)
        self.webview.loadFinished.connect(self._load_finished)


    ################################################################################################################
    # Configure UI methods
    #
    def configure_webview_inspector_ui(self):
        if self.plugin_prefs.get('inspector_enabled'):
            self.webview.setMinimumSize(QSize(600, 300))
            self.inspector = QWebInspector()
            self.inspector.setMinimumSize(QSize(600, 300))
            self.inspector.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
            self.l.addWidget(self.inspector)
            self.inspector.setPage(self.webview.page())
        else:
            self.webview.setMinimumSize(QSize(600, 600))
            if self.inspector is not None:
                self.l.removeWidget(self.inspector)
                self.inspector.setParent(None)
                self.inspector = None


    def save_settings(self):
        self.plugin_prefs.set('inspector_enabled', self.inspector_checkbox.isChecked())
        self.plugin_prefs.set('beta_mode', self.beta_checkbox.isChecked())

        # # If restart needed, inform user
        if self.restart_required:
            # do_restart = show_restart_warning('Restart calibre for the changes to be applied.',
            #                                   parent=self.l)
            # if do_restart:
            #     self.gui.quit(restart=True)

            # TODO: figure out if theres a way to call self.gui.quit()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Restart Required")
            msg.setInformativeText("A configuration change requires you to restart Calibre, You should do so now,")
            msg.setWindowTitle("Restart Required")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()



    def validate(self):
        # TODO: validate the that the api_endpoint and web endpoint are valid urls.
        return True


    ################################################################################################################
    # Event Handlers
    #
    def _url_changed(self, url):
        logger.debug(sys._getframe().f_code.co_name, url)

    def _load_finished(self, ok):
        logger.debug(sys._getframe().f_code.co_name, ok)
        if self.webview.page().mainFrame().url() == self.config_url:
            logger.debug("Loading finished and the url is the same as the desired destination url, ", self.config_url)
            self.webview.page().mainFrame().evaluateJavaScript("""
            console.log("GET LOCALSTORAGE TOKEN")
            """)
            token = self.webview.page().mainFrame().evaluateJavaScript("""
            localStorage.getItem('id_token');
            """)
            logger.debug("Got JWT Token", token)
            self.plugin_prefs.set('token', token)

    def _set_restart_required(self, state):
        '''
        Set restart_required flag to show show dialog when closing dialog
        '''

        logger.debug(sys._getframe().f_code.co_name, "restart required")
        self.restart_required = True

    def _beta_mode_changed(self, state):
        logger.debug(sys._getframe().f_code.co_name, self.beta_checkbox.isChecked())
        self.plugin_prefs.set('beta_mode', self.beta_checkbox.isChecked())

        # if the beta mode has changed, we need to reset the api endpoints, and then wipe the token (not valid between envs)
        self.plugin_prefs.set('token', '')
        if self.plugin_prefs.get('beta_mode'):
            self.plugin_prefs.set('api_base', beta_api_base)
            self.plugin_prefs.set('web_base', beta_web_base)
        else:
            self.plugin_prefs.set('api_base', master_api_base)
            self.plugin_prefs.set('web_base', master_web_base)

        # after we reset the token, we need to generate a new QTWebView with the new config, and then reload the login page.
        self.config_url = QUrl(self.plugin_prefs.get('web_base')+'/storage')

        self.webview.set_bearer_token(self.plugin_prefs.get('token'))
        self.webview.load(self.config_url)


    def _inspector_enabled_changed(self, state):
        logger.debug(sys._getframe().f_code.co_name, self.inspector_checkbox.isChecked())
        self.plugin_prefs.set('inspector_enabled', self.inspector_checkbox.isChecked())
        self.configure_webview_inspector_ui()

class QTWebView(QWebView):

    def __init__(self, parent=None, bearer_token=None):
        super(QWebView,self).__init__(parent)
        page = QTWebPage(bearer_token=bearer_token)
        self.setPage(page)

    def set_bearer_token(self, bearer_token=None):
        self.bearer_token = bearer_token
        self.page().set_bearer_token(bearer_token)


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

    def set_bearer_token(self, bearer_token=None):
        self.bearer_token = bearer_token
        self.nam.set_bearer_token(bearer_token)

    def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
        logger.debug(sys._getframe().f_code.co_name, "(%s:%d): %s" % (sourceID, lineNumber, msg))

    def acceptNavigationRequest(self, frame, request, type):
        logger.debug(sys._getframe().f_code.co_name, request.url(), type)

        origin = frame.securityOrigin()
        logger.debug("Setting new security origin", origin.host())

        self.nam = QTNetworkManager(bearer_token=self.bearer_token,frame_origin=origin)
        self.setNetworkAccessManager(self.nam)
        return True



class QTNetworkManager(QNetworkAccessManager):

    def __init__(self, bearer_token=None, frame_origin=None):
        super(QNetworkAccessManager,self).__init__()
        self.bearer_token = bearer_token
        self.sslErrors.connect(self._ssl_errors)
        self.frame_origin = frame_origin



    def set_bearer_token(self, bearer_token=None):
        self.bearer_token = bearer_token

    def createRequest(self, operation, request, data):
        logger.debug(sys._getframe().f_code.co_name)

        request_host = request.url().host()
        request_path = request.url().path()

        quietthyme_host = QUrl(prefs['web_base']).host()

        if self.bearer_token and (quietthyme_host == request_host): #and not(request_path.startswith('/link/callback')):
            logger.debug("Adding QT Auth header", request.url())
            request.setRawHeader("Authorization", "Bearer %s" % self.bearer_token)

        certs = QSslSocket.systemCaCertificates()
        sslCfg = QSslConfiguration.defaultConfiguration()
        sslCfg.setProtocol(QSsl.TlsV1_0)
        sslCfg.setCaCertificates(certs)
        request.setSslConfiguration(sslCfg)

        if self.frame_origin:
            #adding the current resource request to the security origin witelist.
            self.frame_origin.addAccessWhitelistEntry("http", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("https", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("qrc", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("data", "", QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("https", request.url().host(), QWebSecurityOrigin.AllowSubdomains)
            self.frame_origin.addAccessWhitelistEntry("http", request.url().host(), QWebSecurityOrigin.AllowSubdomains)

        logger.debug("Requesting:", request.url())

        reply = super(QTNetworkManager, self).createRequest(operation, request, data)

        reply.sslErrors.connect(self._reply_ssl_errors)
        reply.error.connect(self._reply_error)
        reply.finished.connect(self._reply_finished)
        return reply

    ################################################################################################################
    # Event Handlers
    def _ssl_errors(self,reply, errors):
        logger.debug("SSL error occured while requesting: %s . Will try to ignore" % reply.url())
        logger.debug("errors: %s", errors)

    def _reply_ssl_errors(self, errors):
        logger.debug("Reply ssl errors:")
        # self.ignoreSslErrors();

    def _reply_error(self, error):
        logger.debug("Reply network error: %s" % error)


    def _reply_finished(self):
        logger.debug("Reply finished")
    # self.ignoreSslErrors();


# For testing ConfigWidget, run from command line:
# cd ~/Documents/calibredev/Marvin_Manager
# calibre-debug config.py
# Search 'Marvin'
if __name__ == '__main__':
    try:
        from PyQt5.Qt import QApplication
    except ImportError:
        from PyQt4.Qt import QApplication

    from calibre.gui2.preferences import test_widget
    app = QApplication([])
    test_widget('Advanced', 'Plugins')