"""
nautilus-image-copypaste -- nautilus extension to copy/paste images between files and clipboard

Author: Reece Hart <reecehart@gmail.com>
License: MIT

MIT License

Copyright (c) 2022 Reece Hart

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import datetime
import itertools
import logging
import os
from pathlib import Path
from urllib.parse import unquote_plus

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Nautilus", "3.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk, Nautilus

_logger = logging.getLogger(__name__)


def copy_image_cb(menuitem, file):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_image(pixbuf)
    _logger.warning(f"Set clipboard from {file}")


def paste_image_cb(menuitem, dir):
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    pixbuf = clipboard.wait_for_image()
    if pixbuf is not None:
        ts = datetime.datetime.utcnow().strftime("%FT%T")
        filename = os.path.join(dir, f"Clipboard {ts}.png")
        pixbuf.savev(filename, "png", (), ())
        _logger.warning(f"Pasted to {filename}")
    else:
        _logger.warning(f"No image on clipboard")


class NautilusImageCopyPaste(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        self.image_extensions = set(
            itertools.chain.from_iterable(
                f.get_extensions() for f in GdkPixbuf.Pixbuf.get_formats()
            )
        )

    def get_file_items(self, window, files):
        if len(files) != 1:
            return
        file = Path(unquote_plus(files[0].get_uri()[7:]))
        if not file.is_file():
            return
        if file.suffix[1:] not in self.image_extensions:
            return
        menuitem = Nautilus.MenuItem(
            name="NautilusImageCopyPasteMP::copy_as_image",
            label="Copy as Image",
            tip=f"Copy {file} to clipboard",
            icon="",
        )
        menuitem.connect("activate", copy_image_cb, str(file))
        return (menuitem,)

    def get_background_items(self, window, folder):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        if clipboard.wait_is_image_available():
            dir = folder.get_location().get_path()
            menuitem = Nautilus.MenuItem(
                name="NautilusImageCopyPasteMP::paste_image",
                label="Paste Image",
                tip="",
                icon="",
            )
            menuitem.connect("activate", paste_image_cb, dir)
            return (menuitem,)
