export PATH=/Applications/calibre.app/Contents/MacOS/:$PATH
calibre-debug -s; calibre-customize -b .; calibre


on linux, calibre configuration is located in
~/.config/calibre/plugins/*


CLI command 
calibre-debug -r "QuietThyme Device Plugin"

#important urls
http://manual.calibre-ebook.com/plugins.html#module-calibre.devices.interface
http://manual.calibre-ebook.com/plugins.html#calibre.devices.usbms.driver.USBMS
    - https://github.com/kovidgoyal/calibre/tree/master/src/calibre/devices/usbms
    - https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/driver.py
    - https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/device.py

https://github.com/kovidgoyal/calibre/blob/master/src/calibre/ebooks/metadata/book/base.py

https://github.com/kovidgoyal/calibre/blob/master/src/calibre/utils/logging.py
https://github.com/kovidgoyal/calibre/blob/v2.21.0/src/calibre/devices/utils.py



Executing arbitrary scripts in the calibre python environment
The calibre-debug command provides a couple of handy switches to execute your own code, with access to the calibre modules:

calibre-debug -c "some python code"
is great for testing a little snippet of code on the command line. It works in the same way as the -c switch to the python interpreter:

calibre-debug playfile.py
can be used to execute your own Python script. It works in the same way as passing the script to the Python interpreter, except that the calibre environment is fully initialized, so you can use all the calibre code in your script. To use command line arguments with your script, use the form:

calibre-debug myscript.py -- --option1 arg1
The -- causes all subsequent arguments to be passed to your script.






#initialization function calls
__init__
startup
is_dynamically_controllable
detect_managed_devices
open
get_device_uid
specialize_global_preferences
card_prefix
set_progress_reporter
set_library_info
set_progress_reporter
get_device_information
card_prefix
free_space
set_progress_reporter
set_library_info
set_progress_reporter
books
books
books
detect_managed_devices
detect_managed_devices
detect_managed_devices
detect_managed_devices
detect_managed_devices
detect_managed_devices
detect_managed_devices
shutdown

