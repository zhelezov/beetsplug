# -*- coding: utf-8 -*-
from beets.plugins import BeetsPlugin

class ForceWritePlugin(BeetsPlugin):
    """Force writing of metadata to files on import"""

    def __init__(self):
        super(ForceWritePlugin, self).__init__()
        self.register_listener('item_imported', self.item_write)
        self.register_listener('album_imported', self.album_write)

        self.config.add({
            'whitelist': ['Opus']
        })

    def item_write(self, lib, item):
        if item.format in self.config['whitelist'].as_str_seq():
            item.write()

    def album_write(self, lib, album):
        for item in album.items():
            self.item_write(lib, item)
