# -*- coding: utf-8 -*-
"""This is a workaround some bug because of which metadata is not written to
disk after the import of Opus files (any files?). Usage of this plugin will
ignore any configuration and forcefully write the changes to files.
"""

from beets.plugins import BeetsPlugin

class ForceWritePlugin(BeetsPlugin):
    """Force writing of metadata to files on import"""

    def __init__(self):
        super(ForceWritePlugin, self).__init__()
        self.register_listener('item_imported', self.item_write)
        self.register_listener('album_imported', self.album_write)

        self.config.add({
            'whitelist': ['*']
        })

    def item_write(self, lib, item):
        whitelist = self.config['whitelist'].as_str_seq()
        if '*' in whitelist or item.format in whitelist:
            item.write()

    def album_write(self, lib, album):
        for item in album.items():
            self.item_write(lib, item)
