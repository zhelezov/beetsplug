# -*- coding: utf-8 -*-

"""The plugin lets you rename untracked audio files located outside of the
beets music library according to a path template. It provides the rename
command.
"""

from beets.plugins import BeetsPlugin
from beets.library import Item
from beets.library import ReadError
from beets import util
from beets import ui

import os


class RenamePlugin(BeetsPlugin):
    def __init__(self):
        super(RenamePlugin, self).__init__()

        self.config.add({
            'template': '$track $title',
            })

    def commands(self):
        rename_cmd = ui.Subcommand('rename', help=u'Rename files based on template')
        rename_cmd.parser.add_option(
                u'-L', u'--follow-links',
                action='store_true', default=False,
                help=u'follow symbolic links to files')
        rename_cmd.parser.add_option(
                u'-n', u'--dry-run',
                action='store_true', default=False,
                help=u'only show the changes to be made')
        rename_cmd.parser.add_option(
                u'-r', u'--recursive',
                action='store_true', default=False,
                help=u'scan directories recursively')
        rename_cmd.parser.add_option(
                u'-R', u'--replace',
                action='store_true', default=False,
                help=u'replace existing files')
        rename_cmd.parser.add_option(
                u'-t', u'--template',
                help=u'override default template: "$track $title"')
        rename_cmd.func = self._rename
        return [rename_cmd]

    def _find_files(self, paths, recursive=False):
        for path in paths:
            path = util.bytestring_path(path)
            if os.path.isdir(util.syspath(path)):
                if recursive:
                    for dirlist in util.sorted_walk(path):
                        for f in dirlist[2]:
                            yield util.bytestring_path(os.path.join(util.syspath(dirlist[0]), util.syspath(f)))
                else:
                    direntries = [os.path.join(util.syspath(path), util.syspath(entry))
                                  for entry in os.listdir(util.syspath(path))]
                    files = [util.bytestring_path(f)
                             for f in direntries
                             if os.path.isfile(util.syspath(f))]
                    files.sort(key=bytes.lower)
                    for fpath in files:
                            yield fpath
            else:
                if os.path.isfile(util.syspath(path)):
                    yield path
                else:
                    self._log.warning(u'Invalid path: {}', util.displayable_path(path))

    def _rename(self, lib, opts, args):
        if not args:
            raise ui.UserError(u'No targets supplied')

        for path in self._find_files(args, opts.recursive):
            if os.path.islink(util.syspath(path)):
                if opts.follow_links:
                    path = util.bytestring_path(os.path.realpath(util.syspath(path)))
                else:
                    continue
            try:
                item = Item.from_path(path)
            except ReadError:
                # skip unrecognized file formats
                continue

            ext = util.text_string(os.path.splitext(util.syspath(path))[1])
            template = opts.template if opts.template else self.config['template'].as_str()
            filename = util.bytestring_path(item.evaluate_template(template, for_path=True) + ext)
            dest = os.path.join(util.syspath(util.ancestry(item.path)[-1]), util.syspath(filename))

            if not opts.dry_run:
                util.mkdirall(dest)
                util.move(item.path, dest, replace=opts.replace)

            if not (util.samefile(item.path, dest) and opts.replace):
                diff = (ui.colordiff(util.displayable_path(item.path), util.displayable_path(dest)))
                if diff[0] != diff[1]:
                    ui.print_(u'    {}\n--> {}'.format(diff[0], diff[1]))
