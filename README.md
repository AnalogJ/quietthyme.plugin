

This is an open source device driver plugin + web server for Calibre. 

##Features:

- It allows you to connect many of the most common cloud storage providers (Dropbox, Google Drive, etc.)
- Clouds are connected as a device drives in Calibre (manage them as you would books on your eReader/iPad)
- Automatically creates a web accessible OPDS server (you don't have to keep your computer on to run Calibre Content Server, or open ports on your router to access your library)
- There's no limit to how many books you can store (you're only limited by your aggregate dropbox/google drive storage space)

##Screenshots:##

_Configuration Screen (Dropbox + Google Drive Connected)_
![http://imgur.com/ehBUVrb](http://i.imgur.com/ehBUVrbl.png)


_Standard Calibre Device Management_
![http://imgur.com/QCmyYVf](http://i.imgur.com/QCmyYVfl.png)


##Storage Providers:

Here's a list of the storage providers that I currently have support for: 
- Dropbox
- Google Drive
- OneDrive (SkyDrive)
- Box

Here's a list of storage providers I want to add support for if there's enough appeal:
- iCloud
- Bittorrent Sync
- OwnCloud

##Requests:
- I need developers who are willing to be beta testers for the plugin. Once we've ironed out any bugs I've missed I'll repost to the plugins forumn. 
- I'm trying to figure out how to customize the UI to display custom icons and labels for the Card and Device buttons, I couldnt really figure out how to do that from the device driver api. Any help here would be appreciated. 

![http://imgur.com/4fHaGDe](http://i.imgur.com/4fHaGDem.png)

- I'm trying to gauge interest in the plugin and see if there's other storage providers I should support. If you have any storage requests, please leave a comment.

Please share this with any developers you think might be interested in beta testing or contributing. The plugin and webserver are both open source, and I would appreciate any help :)

-Jason


##Installation Instructions

- Download the QuietThyme Device Plugin.zip file
- Open Calibre
- Open Preferences
- Under Advanced, click "Plugins"
- Click "Load Plugin from File"
- Select the zip file and click "Open"
- In the Preferences - Plugin list, select "QuietThyme Device Plugin"
- Click "Customize plugin"
- Record your Catalog URL (This is your OPDS url)
- Connect your Cloud Storage provider by clicking the "Connect" button under either Dropbox, Google Drive, etc.
- Approve the connection by signing into your service
- Once your Storage provider is connected, click Ok
- Close all Preferences windows


##Usage Instructions
With QuietThyme installed, you'll see a few extra menu items. It is incredibly simple to store your books in your cloud storage. 

- Right click on any book in your library and select "Send to device"
- Send to "Main Memory" 
- On your OPDS compatible ebook reader, open up your Catalog URL
- You should see your new book available for download with all its metadata and cover art. 





# Testing
export PATH=/Applications/calibre.app/Contents/MacOS/:$PATH
calibre-debug -s; calibre-customize -b .; calibre
calibre-debug test/test_quietthymedeviceplugin.py

on linux, calibre configuration is located in
~/.config/calibre/plugins/*

on mac, calibre configuration is located in
~/Library/Preferences/calibre/plugins/*

log path is:
/tmp/plugin.quietthyme.calibre.log


CLI command 
calibre-debug -r "QuietThyme Device Plugin"

#Important urls
- http://manual.calibre-ebook.com/plugins.html#module-calibre.devices.interface
- http://manual.calibre-ebook.com/plugins.html#calibre.devices.usbms.driver.USBMS
    - https://github.com/kovidgoyal/calibre/tree/master/src/calibre/devices/usbms
    - https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/driver.py
    - https://github.com/kovidgoyal/calibre/blob/master/src/calibre/devices/usbms/device.py
- https://github.com/kovidgoyal/calibre/blob/master/src/calibre/ebooks/metadata/book/base.py

- https://github.com/kovidgoyal/calibre/blob/master/src/calibre/utils/logging.py
- https://github.com/kovidgoyal/calibre/blob/v2.21.0/src/calibre/devices/utils.py



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
