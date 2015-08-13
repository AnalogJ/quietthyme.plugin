import unittest
from PyQt5.Qt import QApplication

from calibre_plugins.quietthyme.config import ConfigWidget, prefs

class TestConfigWidget(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.config = ConfigWidget()

    def test_init(self):
        #ensure that we don't accidentally commit and package with debug mode enabled.
        self.assertEqual(prefs.defaults['debug_mode'], False)
        self.assertEqual(prefs.defaults['api_base'], 'build.quietthyme.com')
        self.assertEqual(prefs.defaults['token'], '')



suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigWidget)
unittest.TextTestRunner(verbosity=2).run(suite)
