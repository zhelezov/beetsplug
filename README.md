# Plugins
## rename

The plugin lets you rename untracked audio files located outside of the beets music library
according to a path template. It provides the `rename` command.

```
$ beet rename --help
Usage: beet rename [options] PATH...

Options:
  -h, --help            show this help message and exit
  -n, --dry-run         only show the changes to be made
  -r, --recursive       scan directories recursively
  -R, --replace         replace existing files
  -t TEMPLATE, --template=TEMPLATE
                        override default template "$track $title"
```

#### Configuration

* **template:** Path template relative to current file location. Default: `$track $title`
