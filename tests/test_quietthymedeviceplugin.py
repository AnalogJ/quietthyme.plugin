import unittest
from calibre_plugins.quietthyme import QuietthymeDevicePlugin

class TestQuietthymeDevicePlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = QuietthymeDevicePlugin(None)

    def test_init(self):
        self.assertEqual(self.plugin.is_connected, False)
        self.assertEqual(self.plugin.is_ejected, False)
        self.assertEqual(self.plugin.current_library_uuid, None)
        self.assertEqual(self.plugin.MANAGES_DEVICE_PRESENCE, True)

    def test_is_customizable(self):
        self.assertEqual(self.plugin.is_customizable(), True)

    def test_detect_managed_devices_can_connect(self):
        self.assertEqual(self.plugin.detect_managed_devices(None, False), True)

    def test_detect_managed_devices_when_connected(self):
        self.plugin.is_connected = True
        self.assertEqual(self.plugin.detect_managed_devices(None, False), True)

    def test_detect_managed_devices_when_ejected(self):
        self.plugin.is_ejected = True
        self.assertEqual(self.plugin.detect_managed_devices(None, False), None)

    def test_open(self):
        self.plugin.open(True, 'test-library-uuid')
        self.assertEqual(self.plugin.is_connected, True)
        self.assertEqual(self.plugin.current_library_uuid, 'test-library-uuid')
        self.assertIsNotNone(self.plugin.qt_settings['main'])
        self.assertEqual(self.plugin.qt_settings['main']['free_space'], 0)
        self.assertEqual(self.plugin.qt_settings['main']['total_space'], 0)

    def test_eject(self):
        self.plugin.eject()
        self.assertEqual(self.plugin.is_connected, False)
        self.assertEqual(self.plugin.is_ejected, True)

    def test_card_prefix_empty(self):
        self.plugin.qt_settings = {}
        self.assertEqual(self.plugin.card_prefix(), (None, None))

    def test_card_prefix_A(self):
        self.plugin.qt_settings = {'A':{'prefix':'dropbox://'}}
        self.assertEqual(self.plugin.card_prefix(), ('dropbox://', None))

    def test_total_space_empty(self):
        self.plugin.qt_settings = {}
        self.assertEqual(self.plugin.total_space(), [0,0,0])

    def test_total_space_populated(self):
        self.plugin.qt_settings = {'main': {'total_space': 1}, 'A': {'total_space': 2}, 'B': {'total_space': 3}}
        self.assertEqual(self.plugin.total_space(), [1, 2, 3])

    def test_free_space_empty(self):
        self.plugin.qt_settings = {}
        self.assertEqual(self.plugin.free_space(), [-1,-1,-1])

    def test_free_space_populated(self):
        self.plugin.qt_settings = {'main': {'free_space': 1}, 'A': {'free_space': 2}, 'B': {'free_space': 3}}
        self.assertEqual(self.plugin.free_space(), [1, 2, 3])

    def test_books(self):
        self.plugin.open(True, 'test-library-uuid')
        self.assertEqual(self.plugin.books(), [])

    def test_convert_oncard_to_cardid(self):

        self.assertEqual(QuietthymeDevicePlugin._convert_oncard_to_cardid(None), 'main')
        self.assertEqual(QuietthymeDevicePlugin._convert_oncard_to_cardid('carda'), 'A')
        self.assertEqual(QuietthymeDevicePlugin._convert_oncard_to_cardid('cardb'), 'B')


suite = unittest.TestLoader().loadTestsFromTestCase(TestQuietthymeDevicePlugin)
unittest.TextTestRunner(verbosity=2).run(suite)
