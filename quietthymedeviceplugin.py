#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

import traceback, os, urllib2, sys, logging
from calibre_plugins.quietthyme import version

# The class that sets and stores the user configured preferences
from calibre_plugins.quietthyme.config import prefs
# The file that contains the Book and Booklist classes
from calibre_plugins.quietthyme.models.book import Book
from calibre_plugins.quietthyme.models.booklist import BookList
#Quietthyme api client.
from calibre_plugins.quietthyme.client.api import ApiClient

# The device error classes.
from calibre.devices.errors import OpenFeedback,OpenFailed

# The class that all Device plugin wrappers must inherit from
#  https://github.com/Philantrop/calibre-ios-reader-applications/blob/master/__init__.py
# http://manual.calibre-ebook.com/plugins.html#module-calibre.devices.interface
from calibre.devices.interface import DevicePlugin

# Used to get the current library name.
from calibre.library import current_library_name

logger = logging.getLogger(__name__)

class QuietthymeDevicePlugin(DevicePlugin):
    '''
    This class is a simple wrapper that provides information about the actual
    plugin class. The actual interface plugin class is called InterfacePlugin
    and is defined in the ui.py file, as specified in the actual_plugin field
    below.

    The reason for having two classes is that it allows the command line
    calibre utilities to run without needing to load the GUI libraries.
    '''
    name                = 'QuietThyme Device Plugin'
    description         = 'QuietThyme storage plugin for Calibre'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Jason Kulatunga'
    version             = version.version_tuple
    minimum_calibre_version = (0, 7, 53)
    gui_name = 'QuietThyme Storage'

    def __init__(self, *args, **kwargs):
        logger.debug(sys._getframe().f_code.co_name)
        DevicePlugin.__init__(self, *args, **kwargs)
        self.progress_reporter = None
        self.current_friendly_name = None
        self.report_progress = lambda x, y: None
        self.current_serial_num = None
        self.gui_name = 'QuietThyme Gui Name'
        self.is_connected = False
        self.is_ejected = False
        self.current_library_uuid = None

        #quietthyme server cache
        self.qt_settings = {}

    """
        Defines the interface that should be implemented by backends that
        communicate with an ebook reader.
        """

    #: Ordered list of supported formats
    FORMATS     = ["epub", "mobi", "pdf", "rtf", "txt", "lrf"]
    # If True, the config dialog will not show the formats box
    HIDE_FORMATS_CONFIG_BOX = False

    #: VENDOR_ID can be either an integer, a list of integers or a dictionary
    #: If it is a dictionary, it must be a dictionary of dictionaries,
    #: of the form::
    #:
    #:   {
    #:    integer_vendor_id : { product_id : [list of BCDs], ... },
    #:    ...
    #:   }
    #:
    VENDOR_ID   = 0x0000

    #: An integer or a list of integers
    PRODUCT_ID  = 0x0000
    #: BCD can be either None to not distinguish between devices based on BCD, or
    #: it can be a list of the BCD numbers of all devices supported by this driver.
    BCD         = None

    #: Height for thumbnails on the device
    THUMBNAIL_HEIGHT = 200
    #: Width for thumbnails on the device. Setting this will force thumbnails
    #: to this size, not preserving aspect ratio. If it is not set, then
    #: the aspect ratio will be preserved and the thumbnail will be no higher
    #: than THUMBNAIL_HEIGHT
    # THUMBNAIL_WIDTH = 68

    #: Compression quality for thumbnails. Set this closer to 100 to have better
    #: quality thumbnails with fewer compression artifacts. Of course, the
    #: thumbnails get larger as well.
    THUMBNAIL_COMPRESSION_QUALITY = 100

    #: Set this to True if the device supports updating cover thumbnails during
    #: sync_booklists. Setting it to true will ask device.py to refresh the
    #: cover thumbnails during book matching
    WANTS_UPDATED_THUMBNAILS = True

    #: Whether the metadata on books can be set via the GUI.
    CAN_SET_METADATA = ['title', 'authors', 'collections']

    #: Whether the device can handle device_db metadata plugboards
    CAN_DO_DEVICE_DB_PLUGBOARD = False

    # Set this to None if the books on the device are files that the GUI can
    # access in order to add the books from the device to the library
    # TODO: this should be set to None
    BACKLOADING_ERROR_MESSAGE = None #_('Cannot get files from this device')

    #: Path separator for paths to books on device
    path_sep = os.sep

    #: Icon for this device
    icon = 'images/icon.png'

    # Encapsulates an annotation fetched from the device
    #UserAnnotation = namedtuple('Annotation','type, value')

    #: GUI displays this as a message if not None. Useful if opening can take a
    #: long time
    #OPEN_FEEDBACK_MESSAGE = 'test message on device open'

    #: Set of extensions that are "virtual books" on the device
    #: and therefore cannot be viewed/saved/added to library
    #: For example: ``frozenset(['kobo'])``
    VIRTUAL_BOOK_EXTENSIONS = frozenset({'ignore'})

    #: Whether to nuke comments in the copy of the book sent to the device. If
    #: not None this should be short string that the comments will be replaced
    #: by.
    NUKE_COMMENTS = None

    #: If True indicates that  this driver completely manages device detection,
    #: ejecting and so forth. If you set this to True, you *must* implement the
    #: detect_managed_devices and debug_managed_device_detection methods.
    #: A driver with this set to true is responsible for detection of devices,
    #: managing a blacklist of devices, a list of ejected devices and so forth.
    #: calibre will periodically call the detect_managed_devices() method and
    #: if it returns a detected device, calibre will call open(). open() will
    #: be called every time a device is returned even is previous calls to open()
    #: failed, therefore the driver must maintain its own blacklist of failed
    #: devices. Similarly, when ejecting, calibre will call eject() and then
    #: assuming the next call to detect_managed_devices() returns None, it will
    #: call post_yank_cleanup().
    MANAGES_DEVICE_PRESENCE = True

    #: If set the True, calibre will call the :meth:`get_driveinfo()` method
    #: after the books lists have been loaded to get the driveinfo.
    SLOW_DRIVEINFO = False

    #: If set to True, calibre will ask the user if they want to manage the
    #: device with calibre, the first time it is detected. If you set this to
    #: True you must implement :meth:`get_device_uid()` and
    #: :meth:`ignore_connected_device()` and
    #: :meth:`get_user_blacklisted_devices` and
    #: :meth:`set_user_blacklisted_devices`
    ASK_TO_ALLOW_CONNECT = False

    #: Set this to a dictionary of the form {'title':title, 'msg':msg, 'det_msg':detailed_msg} to have calibre popup
    #: a message to the user after some callbacks are run (currently only upload_books).
    #: Be careful to not spam the user with too many messages. This variable is checked after *every* callback,
    #: so only set it when you really need to.
    user_feedback_after_callback = None

    def is_usb_connected(self, devices_on_system, debug=False,
                         only_presence=False):
        '''
        Return True, device_info if a device handled by this plugin is currently connected.
        We manage device presence ourselves, so this method should always return False
        :param devices_on_system: List of devices currently connected

        '''
        logger.debug(sys._getframe().f_code.co_name)
        #TODO: no device_info sent. what does that acutally look like.
        return False

    def detect_managed_devices(self, devices_on_system, force_refresh=False):
        '''
        Called only if MANAGES_DEVICE_PRESENCE is True.

        Scan for devices that this driver can handle. Should return a device
        object if a device is found. This object will be passed to the open()
        method as the connected_device. If no device is found, return None. The
        returned object can be anything, calibre does not use it, it is only
        passed to open().

        This method is called periodically by the GUI, so make sure it is not
        too resource intensive. Use a cache to avoid repeatedly scanning the
        system.

        :param devices_on_system: Set of USB devices found on the system.

        :param force_refresh: If True and the driver uses a cache to prevent
                              repeated scanning, the cache must be flushed.

        '''
        #logger.debug(sys._getframe().f_code.co_name)
        if (not self.is_connected) and (not self.is_ejected):
            # check if the user is connected to the internet.
            try:
                urllib2.urlopen('http://www.google.com', timeout=1)
                # The user has not ejected Quietthyme,  doesnt have an active connection and has a valid internet connection.
                # Attempt to open a new connection to the "device"
                return True
            except urllib2.URLError:
                logger.warn('Not connected to the internet, cannot open Quietthyme plugin')
                return None
        elif self.is_connected:
            #the device is already connected, skip so that open is not called repeatedly.
            return True
        else:
            #the device has been ejected, or is no longer connected.
            return None

    def debug_managed_device_detection(self, devices_on_system, output):
        '''
        Called only if MANAGES_DEVICE_PRESENCE is True.

        Should write information about the devices detected on the system to
        output, which is a file like object.

        Should return True if a device was detected and successfully opened,
        otherwise False.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        return True

        # }}}

    def reset(self, key='-1', log_packets=False, report_progress=None,
              detected_device=None):
        """
        :param key: The key to unlock the device
        :param log_packets: If true the packet stream to/from the device is logged
        :param report_progress: Function that is called with a % progress
                                (number between 0 and 100) for various tasks
                                If it is called with -1 that means that the
                                task does not have any progress information
        :param detected_device: Device information from the device scanner

        """
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def can_handle_windows(self, device_id, debug=False):
        '''
        Optional method to perform further checks on a device to see if this driver
        is capable of handling it. If it is not it should return False. This method
        is only called after the vendor, product ids and the bcd have matched, so
        it can do some relatively time intensive checks. The default implementation
        returns True. This method is called only on windows. See also
        :meth:`can_handle`.

        :param device_info: On windows a device ID string. On Unix a tuple of
                            ``(vendor_id, product_id, bcd)``.

        '''
        logger.debug(sys._getframe().f_code.co_name)
        return True

    def can_handle(self, device_info, debug=False):
        '''
        Unix version of :meth:`can_handle_windows`

        :param device_info: Is a tuple of (vid, pid, bcd, manufacturer, product,
                            serial number)

        '''
        logger.debug(sys._getframe().f_code.co_name)

        return True

    def open(self, connected_device, library_uuid):
        '''
        Perform any device specific initialization. Called after the device is
        detected but before any other functions that communicate with the device.
        For example: For devices that present themselves as USB Mass storage
        devices, this method would be responsible for mounting the device or
        if the device has been automounted, for finding out where it has been
        mounted. The method :meth:`calibre.devices.usbms.device.Device.open` has
        an implementation of
        this function that should serve as a good example for USB Mass storage
        devices.

        This method can raise an OpenFeedback exception to display a message to
        the user.

        :param connected_device: The device that we are trying to open. It is
            a tuple of (vendor id, product id, bcd, manufacturer name, product
            name, device serial number). However, some devices have no serial
            number and on windows only the first three fields are present, the
            rest are None.

        :param library_uuid: The UUID of the current calibre library. Can be
            None if there is no library (for example when used from the command
            line).

        '''
        logger.debug(sys._getframe().f_code.co_name)

        # At this point we know that the user has a valid network connection.
        if not prefs['token']:
           # if there is no access_token set, the user hasn't logged in. We can't do anything.
           raise OpenFeedback('QuietThyme has not been authorized on this machine. Please open the plugin preferences to login.')

        # response = ApiClient().auth(library_uuid, current_library_name())
        #
        # #if everything is successful set is_connected to true.
        # if not response['success']:
        #     raise OpenFeedback(response['error_msg'])
        # else:
        #     prefs['token'] = response['data']['token']
        # self.is_connected = response['success']

        status_response = ApiClient().status(library_uuid, current_library_name())
        if not status_response['success']:
            # if an error occurs because token is invalid (401) then remove it.
            if status_response.get('data', {}).get('errorMessage', {}).get('code', 0) == 401:
                prefs.pop('token', None) #delete the token key.
            raise OpenFeedback(status_response['error_msg'])
        self.is_connected = status_response['success']
            #store the settings in memory
        self.current_library_uuid = library_uuid
        #mimic from
        #https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/driver.py
        #https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/device.py
        self.qt_settings = status_response['data']['settings']
        #return True

    def eject(self):
        '''
        Un-mount / eject the device from the OS. This does not check if there
        are pending GUI jobs that need to communicate with the device.

        NOTE: That this method may not be called on the same thread as the rest
        of the device methods.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        self.is_connected = False
        self.is_ejected = True

    def post_yank_cleanup(self):
        '''
        Called if the user yanks the device without ejecting it first.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        raise NotImplementedError()

    def set_progress_reporter(self, report_progress):
        '''
        Set a function to report progress information.

        :param report_progress: Function that is called with a % progress
                                (number between 0 and 100) for various tasks
                                If it is called with -1 that means that the
                                task does not have any progress information

        '''
        logger.debug(sys._getframe().f_code.co_name)
        self.report_progress = report_progress

    def get_device_information(self, end_session=True):
        """
        Ask device for device information. See L{DeviceInfoQuery}.

        :return: (device name, device version, software version on device, mime type)
                 The tuple can optionally have a fifth element, which is a
                 drive information dictionary. See usbms.driver for an example.

        """
        logger.debug(sys._getframe().f_code.co_name)

        self.report_progress(1.0, 'Get device information...')
        return (self.qt_settings.get('device_name', 'QuietThyme'),
                self.qt_settings.get('version', ''),
                self.qt_settings.get('version', ''),
                'application/octet-stream',
                self.qt_settings)

    # Device information {{{
    # def _update_drive_info(self, storage, location_code, name=None):
    #     from calibre.utils.date import isoformat, now
    #     from calibre.utils.config import from_json, to_json
    #     import uuid
    #     f = storage.find_path((self.DRIVEINFO,))
    #     dinfo = {}
    #     if f is not None:
    #         try:
    #             stream = self.get_mtp_file(f)
    #             dinfo = json.load(stream, object_hook=from_json)
    #         except:
    #             prints('Failed to load existing driveinfo.calibre file, with error:')
    #             traceback.print_exc()
    #             dinfo = {}
    #     if dinfo.get('device_store_uuid', None) is None:
    #         dinfo['device_store_uuid'] = unicode(uuid.uuid4())
    #     if dinfo.get('device_name', None) is None:
    #         dinfo['device_name'] = self.current_friendly_name
    #     if name is not None:
    #         dinfo['device_name'] = name
    #     dinfo['location_code'] = location_code
    #     dinfo['last_library_uuid'] = getattr(self, 'current_library_uuid', None)
    #     dinfo['calibre_version'] = '.'.join([unicode(i) for i in numeric_version])
    #     dinfo['date_last_connected'] = isoformat(now())
    #     dinfo['mtp_prefix'] = storage.storage_prefix
    #     raw = json.dumps(dinfo, default=to_json)
    #     self.put_file(storage, self.DRIVEINFO, BytesIO(raw), len(raw))
    #     self.driveinfo[location_code] = dinfo

    def get_driveinfo(self):
        '''
        Return the driveinfo dictionary. Usually called from
        get_device_information(), but if loading the driveinfo is slow for this
        driver, then it should set SLOW_DRIVEINFO. In this case, this method
        will be called by calibre after the book lists have been loaded. Note
        that it is not called on the device thread, so the driver should cache
        the drive info in the books() method and this function should return
        the cached data.
        '''
        # if not self.driveinfo:
        #     self.driveinfo = {}
        #     for sid, location_code in ( (self._main_id, 'main'), (self._carda_id,
        #                                                           'A'), (self._cardb_id, 'B')):
        #         if sid is None: continue
        #         self._update_drive_info(self.filesystem_cache.storage(sid), location_code)
        # return self.driveinfo
        logger.debug(sys._getframe().f_code.co_name)
        raise NotImplementedError()


    def card_prefix(self, end_session=True):
        '''
        Return a 2 element list of the prefix to paths on the cards.
        If no card is present None is set for the card's prefix.
        E.G.
        ('/place', '/place2')
        (None, 'place2')
        ('place', None)
        (None, None)
        '''
        # return  (self._carda_id, self._cardb_id)
        logger.debug(sys._getframe().f_code.co_name)

        return (self.qt_settings.get('A',{}).get('prefix',None), self.qt_settings.get('B',{}).get('prefix',None))

    def total_space(self, end_session=True):
        """
        Get total space available on the mountpoints:
            1. Main memory
            2. Memory Card A
            3. Memory Card B

        :return: A 3 element list with total space in bytes of (1, 2, 3). If a
                 particular device doesn't have any of these locations it should return 0.

        """
        logger.debug(sys._getframe().f_code.co_name)

        return [
            self.qt_settings.get('main',{}).get('total_space',0),
            self.qt_settings.get('A',{}).get('total_space',0),
            self.qt_settings.get('B',{}).get('total_space',0)
        ]

    def free_space(self, end_session=True):
        """
        Get free space available on the mountpoints:
          1. Main memory
          2. Card A
          3. Card B

        :return: A 3 element list with free space in bytes of (1, 2, 3). If a
                 particular device doesn't have any of these locations it should return -1.

        """
        logger.debug(sys._getframe().f_code.co_name)

        return [
            self.qt_settings.get('main',{}).get('free_space',-1),
            self.qt_settings.get('A',{}).get('free_space',-1),
            self.qt_settings.get('B',{}).get('free_space',-1)
        ]
    # }}}

    def books(self, oncard=None, end_session=True):
        """
        Return a list of ebooks on the device.

        :param oncard:  If 'carda' or 'cardb' return a list of ebooks on the
                        specific storage card, otherwise return list of ebooks
                        in main memory of device. If a card is specified and no
                        books are on the card return empty list.

        :return: A BookList.

        """
        logger.debug(sys._getframe().f_code.co_name)
        card_id = self._convert_oncard_to_cardid(oncard)
        storage_type = self.qt_settings.get(card_id,{}).get('storage_type',"")
        storage_id = self.qt_settings.get(card_id,{}).get('storage_id',None)
        if storage_id is not None:
            qt_response = ApiClient().books_all(storage_id)['data']
            qt_booklist = qt_response['Items']
        else:
            qt_booklist = []

        booklist = BookList(None, None, None)

        placeholderBook = Book()
        placeholderBook.title = "## {0} books ##".format(storage_type.capitalize())
        placeholderBook.authors = ['QuietThyme']
        placeholderBook.comments = "All Books in this list are actually stored on {0} cloud storage".format(storage_type.capitalize())

        placeholderBook.size = 0
        placeholderBook.thumbnail = get_resources("images/{0}.png".format(storage_type))
        placeholderBook.tags = [storage_type]
        placeholderBook.identifiers = {}
        placeholderBook.path = "placeholder.ignore"


        booklist.add_book(placeholderBook, False)


        for i, qt_metadata in enumerate(qt_booklist):
            self.report_progress((i+1) / float(len(qt_booklist)), _('Loading books from device...'))
            if qt_metadata['storage_identifier']:
                #logger.debug(qt_metadata)
                booklist.add_book(Book.from_quietthyme_metadata(qt_metadata), False)
        self.report_progress(1.0, _('Loaded book from device'))
        return booklist

    def upload_books(self, files, names, on_card=None, end_session=True,
                     metadata=None):
        '''
        Upload a list of books to the device. If a file already
        exists on the device, it should be replaced.
        This method should raise a :class:`FreeSpaceError` if there is not enough
        free space on the device. The text of the FreeSpaceError must contain the
        word "card" if ``on_card`` is not None otherwise it must contain the word "memory".

        :param files: A list of paths
        :param names: A list of file names that the books should have
                      once uploaded to the device. len(names) == len(files)
        :param metadata: If not None, it is a list of :class:`Metadata` objects.
                         The idea is to use the metadata to determine where on the device to
                         put the book. len(metadata) == len(files). Apart from the regular
                         cover (path to cover), there may also be a thumbnail attribute, which should
                         be used in preference. The thumbnail attribute is of the form
                         (width, height, cover_data as jpeg).

        :return: A list of 3-element tuples. The list is meant to be passed
                 to :meth:`add_books_to_metadata`.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        logger.debug(files, names, on_card, metadata[0].__unicode__())

        card_id = self._convert_oncard_to_cardid(on_card)
        dest_info = []
        names = iter(names)
        metadata = iter(metadata)
        for i, local_filepath in enumerate(files):
            local_metadata, fname = metadata.next(), names.next()

            qt_book_data = self._upload_book(local_filepath, self.qt_settings[card_id].get('storage_id', 'quietthyme'), local_metadata,  replace_file=True)
            try:

                if local_metadata.get('cover'):
                    # dest_info['image'] = self._upload_cover(qt_metadata,local_metadata)
                    qt_book_data = self._upload_cover(qt_book_data, local_metadata)

            except Exception as inst:  # Failure to upload cover is not catastrophic
                # import traceback
                # traceback.print_exc()
                logger.error('could not upload cover %s' % inst)

            dest_info.append((card_id, qt_book_data)) #pass the calibre metadata (mdata) as a backup, should not be used though...
            self.report_progress((i+1) / float(len(files)), _('Transferring books to device...'))

        self.report_progress(1.0, _('Transferring books to device...'))
        logger.debug('finished uploading %d books'%(len(files)))
        logger.debug(dest_info)
        return dest_info

    def add_books_to_metadata(self, dest_info, metadata, booklists):
        '''
        Add locations to the booklists. This function must not communicate with
        the device.

        :param dest_info: Result of a call to L{upload_books}
        :param metadata: List of :class:`Metadata` objects, same as for
                         :meth:`upload_books`.
        :param booklists: A tuple containing the result of calls to
                          (:meth:`books(oncard=None)`,
                          :meth:`books(oncard='carda')`,
                          :meth`books(oncard='cardb')`).

        '''
        logger.debug(sys._getframe().f_code.co_name)
        logger.debug('USBMS: adding metadata for %d books'%(len(metadata)))

        metadata = iter(metadata)
        for i, location in enumerate(dest_info):
            self.report_progress((i+1) / float(len(dest_info)), _('Adding books to device metadata listing...'))
            local_metadata = metadata.next()
            blist = 2 if location[0] == 'B' else 1 if location[0] == 'A' else 0

            try:
                book = Book.from_quietthyme_metadata(location[1])
            except StandardError, e:

                logger.debug('An error occured while adding book via QT data, using calibre data')
                logger.debug(str(e))
                import traceback
                logger.debug(traceback.format_exc())
                book = Book.from_calibre_metadata(local_metadata)

            b = booklists[blist].add_book(book, replace_metadata=True)
            if b:
                b._new_book = True
        self.report_progress(1.0, _('Adding books to device metadata listing...'))
        logger.debug('finished adding metadata')

    def delete_books(self, paths, end_session=True):
        '''
        Delete books at paths on device.
        '''
        from urlparse import urlparse
        logger.debug(sys._getframe().f_code.co_name)
        logger.debug(paths)
        for i, qt_storage_id in enumerate(paths):
            self.report_progress((i+1) / float(len(paths)), _('Deleting books from QuietThyme...'))
            logger.debug(qt_storage_id)
            if qt_storage_id == 'placeholder.ignore':
                continue
            ApiClient().destroy_book(qt_storage_id)
        self.report_progress(1.0, _('Removing books from QuietThyme...'))

    def remove_books_from_metadata(self, paths, booklists):
        '''
        Remove books from the metadata list. This function must not communicate
        with the device.

        :param paths: paths to books on the device.
        :param booklists: A tuple containing the result of calls to
                          (:meth:`books(oncard=None)`,
                          :meth:`books(oncard='carda')`,
                          :meth`books(oncard='cardb')`).

        '''
        logger.debug(sys._getframe().f_code.co_name)
        for i, path in enumerate(paths):
            self.report_progress((i+1) / float(len(paths)), _('Removing books from Calibre metadata cache...'))
            for bl in booklists:
                for book in bl:
                    if path.endswith(book.path):
                        bl.remove_book(book)

        self.report_progress(1.0, _('Removing books from Calibre metadata cache...'))

    def sync_booklists(self, booklists, end_session=True):
        '''
        Update metadata on device.

        :param booklists: A tuple containing the result of calls to
                          (:meth:`books(oncard=None)`,
                          :meth:`books(oncard='carda')`,
                          :meth`books(oncard='cardb')`).

        '''
        #TODO: look into exatly what we should be doing here
        #TODO: our metadata has already been synced, when the book was uploaded, it pushed the metadata up
        #TODO: unless this method is more generic, and is called in other places, then we will have to iterate over the
        #TODO: booklists and do a ton of api requests :(
        logger.debug(sys._getframe().f_code.co_name)

        #TODO: use the quietthyme api to push metadata up

        # Clear the _new_book indication, as we are supposed to be done with
        # adding books at this point
        for blist in booklists:
            if blist is not None:
                for book in blist:
                    book._new_book = False

        self.report_progress(1.0, _('Sending metadata to device...'))
        logger.debug('finished sync_booklists')

    def get_file(self, path, outfile, end_session=True):
        '''
        Read the file at ``path`` on the device and write it to outfile.

        :param outfile: file object like ``sys.stdout`` or the result of an
                       :func:`open` call.

        '''
        logger.debug(sys._getframe().f_code.co_name)
        outfile.write(ApiClient().download_bookstorage(path))

    def save_settings(self, config_widget):
        '''
        Save the settings specified by the user with config_widget.

        :param config_widget: The widget returned by :meth:`config_widget`.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        config_widget.save_settings()
        self.is_connected = False #force plugin to be re-opened after a user closes the config window.

    def settings(self):
        '''
        Should return an opts object. The opts object should have at least one
        attribute `format_map` which is an ordered list of formats for the
        device.
        '''
        logger.debug(sys._getframe().f_code.co_name)

        class Settings():
            def __init__(self, format_map=[]):
                self.format_map = format_map

        return Settings(self.FORMATS)

    def set_plugboards(self, plugboards, pb_func):
        '''
        provide the driver the current set of plugboards and a function to
        select a specific plugboard. This method is called immediately before
        add_books and sync_booklists.

        pb_func is a callable with the following signature::
            def pb_func(device_name, format, plugboards)

        You give it the current device name (either the class name or
        DEVICE_PLUGBOARD_NAME), the format you are interested in (a 'real'
        format or 'device_db'), and the plugboards (you were given those by
        set_plugboards, the same place you got this method).

        :return: None or a single plugboard instance.

        '''
        pass

    def set_driveinfo_name(self, location_code, name):
        '''
        Set the device name in the driveinfo file to 'name'. This setting will
        persist until the file is re-created or the name is changed again.

        Non-disk devices should implement this method based on the location
        codes returned by the get_device_information() method.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        sid = {'main':self._main_id, 'A':self._carda_id,
               'B':self._cardb_id}.get(location_code, None)
        if sid is None:
            return
        self._update_drive_info(self.filesystem_cache.storage(sid),
                                location_code, name=name)

    def prepare_addable_books(self, paths):
        '''
        Given a list of paths, returns another list of paths. These paths
        point to addable versions of the books.

        If there is an error preparing a book, then instead of a path, the
        position in the returned list for that book should be a three tuple:
        (original_path, the exception instance, traceback)
        '''
        logger.debug(sys._getframe().f_code.co_name)
        return paths

    def startup(self):
        '''
        Called when calibre is is starting the device. Do any initialization
        required. Note that multiple instances of the class can be instantiated,
        and thus __init__ can be called multiple times, but only one instance
        will have this method called. This method is called on the device
        thread, not the GUI thread.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass


    def shutdown(self):
        '''
        Called when calibre is shutting down, either for good or in preparation
        to restart. Do any cleanup required. This method is called on the
        device thread, not the GUI thread.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def get_device_uid(self):
        '''
        Must return a unique id for the currently connected device (this is
        called immediately after a successful call to open()). You must
        implement this method if you set ASK_TO_ALLOW_CONNECT = True
        '''
        logger.debug(sys._getframe().f_code.co_name)
        raise NotImplementedError()

    def ignore_connected_device(self, uid):
        '''
        Should ignore the device identified by uid (the result of a call to
        get_device_uid()) in the future. You must implement this method if you
        set ASK_TO_ALLOW_CONNECT = True. Note that this function is called
        immediately after open(), so if open() caches some state, the driver
        should reset that state.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        raise NotImplementedError()

    def get_user_blacklisted_devices(self):
        '''
        Return map of device uid to friendly name for all devices that the user
        has asked to be ignored.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        return {}

    def set_user_blacklisted_devices(self, devices):
        '''
        Set the list of device uids that should be ignored by this driver.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def specialize_global_preferences(self, device_prefs):
        '''
        Implement this method if your device wants to override a particular
        preference. You must ensure that all call sites that want a preference
        that can be overridden use device_prefs['something'] instead
        of prefs['something']. Your
        method should call device_prefs.set_overrides(pref=val, pref=val, ...).
        Currently used for:
        metadata management (prefs['manage_device_metadata'])
        '''
        logger.debug(sys._getframe().f_code.co_name)
        device_prefs.set_overrides()

    def set_library_info(self, library_name, library_uuid, field_metadata):
        '''
        Implement this method if you want information about the current calibre
        library. This method is called at startup and when the calibre library
        changes while connected.
        '''
        #TODO: Library info changed, relogin/get a new token.
        logger.debug(sys._getframe().f_code.co_name)
        logger.debug("LIBRARY INFO CHANGED",library_name, library_uuid, field_metadata)
        self.current_library_uuid = library_uuid
        self.is_connected = False
        pass

        # Dynamic control interface.
        # The following methods are probably called on the GUI thread. Any driver
        # that implements these methods must take pains to be thread safe, because
        # the device_manager might be using the driver at the same time that one of
        # these methods is called.

    def is_dynamically_controllable(self):
        '''
        Called by the device manager when starting plugins. If this method returns
        a string, then a) it supports the device manager's dynamic control
        interface, and b) that name is to be used when talking to the plugin.

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        #TODO: use this method to create a customized UI.
        return None

    def start_plugin(self):
        '''
        This method is called to start the plugin. The plugin should begin
        to accept device connections however it does that. If the plugin is
        already accepting connections, then do nothing.

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def stop_plugin(self):
        '''
        This method is called to stop the plugin. The plugin should no longer
        accept connections, and should cleanup behind itself. It is likely that
        this method should call shutdown. If the plugin is already not accepting
        connections, then do nothing.

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def get_option(self, opt_string, default=None):
        '''
        Return the value of the option indicated by opt_string. This method can
        be called when the plugin is not started. Return None if the option does
        not exist.

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        return default

    def set_option(self, opt_string, opt_value):
        '''
        Set the value of the option indicated by opt_string. This method can
        be called when the plugin is not started.

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        logger.debug(sys._getframe().f_code.co_name)
        pass

    def is_running(self):
        '''
        Return True if the plugin is started, otherwise false

        This method can be called on the GUI thread. A driver that implements
        this method must be thread safe.
        '''
        return True

    def synchronize_with_db(self, db, book_id, book_metadata, first_call):
        '''
        Called during book matching when a book on the device is matched with
        a book in calibre's db. The method is responsible for syncronizing
        data from the device to calibre's db (if needed).

        The method must return a two-value tuple. The first value is a set of
        calibre book ids changed if calibre's database was changed or None if the
        database was not changed. If the first value is an empty set then the
        metadata for the book on the device is updated with calibre's metadata
        and given back to the device, but no GUI refresh of that book is done.
        This is useful when the calibre data is correct but must be sent to the
        device.

        The second value is itself a 2-value tuple. The first value in the tuple
        specifies whether a book format should be sent to the device. The intent
        is to permit verifying that the book on the device is the same as the
        book in calibre. This value must be None if no book is to be sent,
        otherwise return the base file name on the device (a string like
        foobar.epub). Be sure to include the extension in the name. The device
        subsystem will construct a send_books job for all books with not- None
        returned values. Note: other than to later retrieve the extension, the
        name is ignored in cases where the device uses a template to generate
        the file name, which most do. The second value in the returned tuple
        indicated whether the format is future-dated. Return True if it is,
        otherwise return False. Calibre will display a dialog to the user
        listing all future dated books.

        Extremely important: this method is called on the GUI thread. It must
        be threadsafe with respect to the device manager's thread.

        book_id: the calibre id for the book in the database.
        book_metadata: the Metadata object for the book coming from the device.
        first_call: True if this is the first call during a sync, False otherwise
        '''
        logger.debug(sys._getframe().f_code.co_name)
        return (None, (None, False))

    ####################################################################################################################
    #Upload Books Helper Functions


    def _create_upload_path(self, prefix, mdata, fname):
        from calibre.devices.utils import create_upload_path
        #TODO: template language http://manual.calibre-ebook.com/template_lang.html


        template = '{author_sort}'
        if mdata.series:
            template += ' - {series}'

        if mdata.series_index:
            template += ' - {series_index}'

        template += ' - {title}'


        filepath = create_upload_path(mdata, fname,template,lambda x: x,
                                      prefix_path=prefix,
                                      maxlen=250,                   #The maximum length of paths created on quietthyme
                                      use_subdirs=True,
                                      news_in_folder=True
                                      )

        return str(filepath)

    def _upload_book(self, local_filepath, storage_id, local_metadata, replace_file=True):
        #TODO: upload the file and metadata to quietthyme. Determine if a new book should be created or replaced.

        qt_book_data = ApiClient().create_book(local_metadata)

        #after creating book metadata, we need to get a signed url so we can upload the book to QuietThyme storage
        qt_filename = self._create_upload_path('',local_metadata, local_filepath)
        qt_filename_base, qt_filename_ext = os.path.splitext(qt_filename)

        qt_storage_metadata = {
            'book_id': qt_book_data['id'],
            'storage_id': storage_id,
            'replace': replace_file,

            #only these parameters will be stored directly
            'storage_size': os.stat(local_filepath).st_size, #storage size in bytes
            'storage_filename': qt_filename_base, # nice filename for UI.=
            'storage_format': qt_filename_ext # file extension
        }

        qt_upload_data = ApiClient().prepare_bookstorage(qt_storage_metadata)
        qt_book_data.update(qt_upload_data['data']['book_data'])

        #TODO: this bookstorage uploader is a bit flimsy
        ApiClient().upload_bookstorage(qt_upload_data['data']['upload_url'], local_filepath)


        return qt_book_data

    def _upload_cover(self, qt_book_data,
                      local_metadata):
        # using the return value of the uploaded book (the book ID) we should upload the cover to QuietThyme storage
        # so that the cover is always available.
        qt_filename = self._create_upload_path('', local_metadata, local_metadata.get('cover'))

        qt_upload_data = ApiClient().prepare_cover_storage(qt_book_data["id"], qt_filename)
        qt_book_data.update(qt_upload_data['data']['book_data'])


        ApiClient().upload_cover(qt_upload_data['data']['upload_url'],
                                                local_metadata.get('cover'))
        return qt_book_data


    ####################################################################################################################
    # Generic Helper Functions

    @classmethod
    def _convert_oncard_to_cardid(cls, oncard):
        if oncard == None:
            return "main"
        elif oncard == "carda":
            return "A"
        elif oncard == "cardb":
            return "B"
        else:
            raise Exception()
