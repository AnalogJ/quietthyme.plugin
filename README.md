
This is an open source device driver plugin + web server for Calibre.

## Features:

- It allows you to connect many of the most common cloud storage providers (Dropbox, Google Drive, etc.)
- Clouds are connected as a device drives in Calibre (manage them as you would books on your eReader/iPad)
- Automatically creates a web accessible OPDS server (you don't have to keep your computer on to run Calibre Content Server, or open ports on your router to access your library)
- There's no limit to how many books you can store (you're only limited by your aggregate dropbox/google drive storage space)

## Screenshots
Here's a quick gif of what you can do with the QuietThyme plugin for Calibre

![](https://raw.githubusercontent.com/AnalogJ/quietthyme.web.src/gh-pages/assets/uservoice/QuietThyme-Library-Manual-Upload.gif)

## Storage Providers:

Here's a list of the storage providers that I currently have support for: 
- Dropbox
- Google Drive
- OneDrive (SkyDrive)
- Box

Here's a list of storage providers I want to add support for if there's enough appeal:
- iCloud
- Bittorrent Sync
- OwnCloud

# Installation
First you'll need to download the latest packaged version of **quiethyme_plugin.zip** from the plugin Github repository: [https://github.com/AnalogJ/quietthyme.plugin/releases](https://github.com/AnalogJ/quietthyme.plugin/releases "Link: https://github.com/AnalogJ/quietthyme.plugin/releases")

![](https://raw.githubusercontent.com/AnalogJ/quietthyme.web.src/gh-pages/assets/uservoice/QuietThyme-Calibre-Download.png)

Once you've done that, you'll need to add the plugin to Calibre.

- Open up Calibre
- Go to the **Preferences** menu
- Under **Advanced**, click **Plugins**
- click **Load Plugin** from file
- Select the **quietthyme_plugin.zip** that you downloaded from Github
- Back on the Plugins page, click **Show only user installed plugins**
- Expand **Device interface plugins**
- Click **Customize plugin**
- Check **Beta Mode**
- Wait for page to reload
- **Login** to QuietThyme
- Once you've logged in, you can hit **OK**
- **Close all** windows and **restart** Calibre

Here's a quick gif showing all the steps above. 

![](https://raw.githubusercontent.com/AnalogJ/quietthyme.web.src/gh-pages/assets/uservoice/QuietThyme-Calibre-Install.gif)

Now that you've done that, you can re-open Calibre, and you'll see the QuietThyme storage drives available as new devices.

Now you can [add books to QuietThyme via Calibre](https://quietthyme.uservoice.com/knowledgebase/articles/123761-how-do-i-upload-ebooks#calibre).


## Usage Instructions
With QuietThyme installed, you'll see a few extra menu items. It is incredibly simple to store your books in your cloud storage. 

- Right click on any book in your library and select "Send to device"
- Send to "Main Memory" 
- On your OPDS compatible ebook reader, open up your Catalog URL
- You should see your new book available for download with all its metadata and cover art. 


## Requests:
- I need developers who are willing to be beta testers for the plugin. Once we've ironed out any bugs I've missed I'll repost to the plugins forumn.
- I'm trying to figure out how to customize the UI to display custom icons and labels for the Card and Device buttons, I couldnt really figure out how to do that from the device driver api. Any help here would be appreciated.

![http://imgur.com/4fHaGDe](http://i.imgur.com/4fHaGDem.png)

- I'm trying to gauge interest in the plugin and see if there's other storage providers I should support. If you have any storage requests, please leave a comment.

Please share this with any developers you think might be interested in beta testing or contributing. The plugin and webserver are both open source, and I would appreciate any help :)

-Jason

