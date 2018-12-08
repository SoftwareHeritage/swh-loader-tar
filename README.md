# SWH Tarball Loader

The Software Heritage Tarball Loader is in charge of ingesting the
directory representation of the tarball into the Software Heritage
archive.

## Configuration

This is the loader's (or task's) configuration file.

*`{/etc/softwareheritage | ~/.config/swh | ~/.swh}`/loader/tar.yml*:

```YAML
working_dir: /home/storage/tmp/
storage:
  cls: remote
  args:
    url: http://localhost:5002/
```

## API

### local

Load local tarball directly from code or python3's toplevel:

``` Python
# Fill in those
repo = '8sync.tar.gz'
tarpath = '/home/storage/tar/%s' % repo
origin = {'url': 'file://%s' % repo, 'type': 'tar'}
visit_date = 'Tue, 3 May 2017 17:16:32 +0200'
last_modified = 'Tue, 10 May 2016 16:16:32 +0200'
import logging
logging.basicConfig(level=logging.DEBUG)

from swh.loader.tar.tasks import LoadTarRepository
l = LoadTarRepository()
l.run_task(origin=origin, visit_date=visit_date,
	       last_modified=last_modified)
```

### remote

Load remote tarball is the same sample

```Python
url = 'https://ftp.gnu.org/gnu/8sync/8sync-0.1.0.tar.gz'
origin = {'url': url, 'type': 'tar'}
visit_date = 'Tue, 3 May 2017 17:16:32 +0200'
last_modified = '2016-04-22 16:35'
import logging
logging.basicConfig(level=logging.DEBUG)

from swh.loader.tar.tasks import LoadTarRepository
l = LoadTarRepository()
l.run_task(origin=origin, visit_date=visit_date,
	       last_modified=last_modified)
```
