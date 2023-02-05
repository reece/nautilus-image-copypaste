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
from typing import List
#from urllib.parse import unquote_plus

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Nautilus", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gdk, GdkPixbuf, GObject, Nautilus, Gtk

_logger = logging.getLogger(__name__)


def get_clipboard():
    # BROKEN. How do I get the clipboard for the current app?  It requires having a widget that is
    # attached to the top-level window.  See
    # https://docs.gtk.org/gtk3/method.Widget.get_clipboard.html#description
    return Gdk.Display().get_clipboard()

def is_image(clipboard):
    return "GdkTexture" in clipboard.get_formats().to_string()

class NautilusImageCopyPaste(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.image_extensions = set(
            itertools.chain.from_iterable(
                f.get_extensions() for f in GdkPixbuf.Pixbuf.get_formats()
            )
        )
        _logger.warn(f"Allowed image extensions: {','.join(sorted(self.image_extensions))}")

    def get_file_items(self, files: List[Nautilus.FileInfo]) -> List[Nautilus.MenuItem]:
        """Return menu items when clicked on a Nautilus icon selection"""
        if len(files) != 1:
            return None
        file = Path(files[0].get_location().get_path())
        if not file.is_file():
            return None
        if file.suffix[1:] not in self.image_extensions:
            return None
        menuitem = Nautilus.MenuItem(
            name="NautilusImageCopyPasteMP::copy_as_image",
            label="Copy image to clipboard",
            tip=f"Copy {file} to clipboard",
            icon="",
        )
        menuitem.connect("activate", self.copy_file_image_to_clipboard, str(file))
        return [menuitem]

    def get_background_items(self, folder: Nautilus.FileInfo) -> List[Nautilus.MenuItem]:
        """Return menu items when the Nautilus background is clicked and an image is on the
        clipboard"""
        clipboard = get_clipboard()
        if is_image(clipboard):
            dir = folder.get_location().get_path()
            menuitem = Nautilus.MenuItem(
                name="NautilusImageCopyPasteMP::paste_image",
                label="Paste clipboard image as file",
                tip="",
                icon="",
            )
            menuitem.connect("activate", self.copy_clipboard_to_file_image, dir)
            return [menuitem]

    def copy_file_image_to_clipboard(self, menuitem: Nautilus.MenuItem, file):
        texture = Gdk.Texture.new_from_filename(file)
        clipboard = get_clipboard()
        clipboard.set(texture)
        _logger.warning(f"Set clipboard from {file}; {texture.get_width()}x{texture.get_height()}")

    def copy_clipboard_to_file_image(self, menuitem: Nautilus.MenuItem, dir):
        clipboard = get_clipboard()

        def update_cb(so, res, user_data):
            texture = clipboard.read_texture_finish(res)
            pixbuf = Gdk.pixbuf_get_from_texture(texture)
            ts = datetime.datetime.utcnow().strftime("%FT%T")
            filename = os.path.join(dir, f"Clipboard {ts}.png")
            pixbuf.savev(filename, "png", (), ())
            _logger.warning(f"Pasted to {filename}")

        clipboard.read_texture_async(
            cancellable=None, callback=update_cb, user_data=None
        )


        
