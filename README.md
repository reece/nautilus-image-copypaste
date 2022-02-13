# nautilus-image-copypaste

Nautilus extension to paste from clipboard to a file and to copy an image from a file to the clipboard.

Once installed:

* Select an image file, open the context menu, and select Copy as Image.  All image extensions supported by GdkPixbuf are supported. [screenshot](data/copy.png)
* With an image on the cliboard, open the background context menu and select Paste Image.  The file will appear as `Cliboard <timestamp>.png`. The path and image format are not customizable (for now). [screenshot](data/paste.png)

## Prerequisites

* GNOME 3.x
* Nautilus 3.x
* python3-nautilus package (`sudo apt install python3-nautilus`)

## Installation from source

    make install
    nautilus -q; nautilus ~

## Development

Contributions welcome.

Use `make install-dev` to install as symlink.  You'll need to restart nautilus to reload.

`NAUTILUS_PYTHON_DEBUG=misc nautilus .` increases nautilus verbosity.

Source code is formatted with black and isort.

## See also

https://github.com/atareao/nautilus-copypaste-images is similar. (I was
unable to make it, or any of the forks, work.)
