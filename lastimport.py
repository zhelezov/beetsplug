# -*- coding: utf-8 -*-
"""Plugin providing a reference to the last successful import. Imported items'
ids are stored in a separate table in the database during import. Provides the
command `lastimport' to list them.
"""

from beets.plugins import BeetsPlugin
from beets.util import normpath
from beets.ui import Subcommand, print_


def import_hook(lib, paths):
    """Store imported items' ids in a database table

    The table is recreated after each import.
    """

    paths = [normpath(path) for path in paths]
    with lib.transaction() as tx:
        sql = """
            DROP TABLE IF EXISTS last_import;
            CREATE TABLE last_import (id INTEGER PRIMARY KEY);
        """
        tx.script(sql)

        params = ', '.join('?' * len(paths))
        sql = """
            INSERT INTO last_import
            SELECT id FROM items WHERE path IN ({})
        """.format(params)
        tx.mutate(sql, paths)


def list_items(lib, opts, args):
    """Print a list of items from the last import

    Output is formatted according to the `format_item' configuration option
    except when the -p switch is used -- prints paths in this case.
    """

    ids = []
    with lib.transaction() as tx:
        sql = 'SELECT id FROM last_import'
        ids = [row['id'] for row in tx.query(sql)]
    for item_id in ids:
        for item in lib.items('id::^{}$'.format(item_id)):
            print_(str(item))


class LastImportPlugin(BeetsPlugin):
    """Keep track of the last imported items"""

    def __init__(self):
        super(LastImportPlugin, self).__init__()
        self.register_listener('import', import_hook)

    def commands(self):
        cmd = Subcommand('lastimport', help=u'list last imported items')
        cmd.parser.add_path_option()
        cmd.func = list_items
        return [cmd]
