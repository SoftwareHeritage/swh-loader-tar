# SWH Tarball Loader

The Software Heritage Tarball Loader is a tool and a library to
uncompress a local tarball and inject into the SWH dataset its tree
representation.

## Configuration

This is the loader's (or task's) configuration file.

*`{/etc/softwareheritage | ~/.config/swh | ~/.swh}`/loader/tar.yml*:

```YAML
extraction_dir: /home/storage/tmp/
storage:
  cls: remote
  args:
    url: http://localhost:5002/
```

## API

Load tarball directly from code or python3's toplevel:

``` Python
# Fill in those
repo = 'loader-tar.tgz'
tarpath = '/home/storage/tar/%s' % repo
origin = {'url': 'ftp://%s' % repo, 'type': 'tar'}
visit_date = 'Tue, 3 May 2017 17:16:32 +0200'
revision = {
    'author': {'name': 'some', 'fullname': 'one', 'email': 'something'},
    'committer': {'name': 'some', 'fullname': 'one', 'email': 'something'},
    'message': '1.0 Released',
    'date': None,
    'committer_date': None,
    'type': 'tar',
}
import logging
logging.basicConfig(level=logging.DEBUG)

from swh.loader.tar.tasks import LoadTarRepository
l = LoadTarRepository()
l.run_task(tar_path=tarpath, origin=origin, visit_date=visit_date,
           revision=revision, branch_name='master')
```

## Celery

Load tarball using celery.

Providing you have a properly configured celery up and running, the
celery worker configuration file needs to be updated:

*`{/etc/softwareheritage | ~/.config/swh | ~/.swh}`/worker.yml*:

``` YAML
task_modules:
  - swh.loader.tar.tasks
task_queues:
  - swh_loader_tar
```

cf. https://forge.softwareheritage.org/diffusion/DCORE/browse/master/README.md
for more details


## Tar Producer

Its job is to compulse from a file or a folder a list of existing
tarballs. From this list, compute the corresponding messages to send
to the broker.

### Configuration

Message producer's configuration file (`tar.yml`):

``` YAML
# Mirror's root directory holding tarballs to load into swh
mirror_root_directory: /srv/storage/space/mirrors/gnu.org/gnu/
# Url scheme prefix used to create the origin url
url_scheme: http://ftp.gnu.org/gnu/
type: ftp

# File containing a subset list tarballs from mirror_root_directory to load.
# The file's format is one absolute path name to a tarball per line.
# NOTE:
# - This file must contain data consistent with the mirror_root_directory
# - if this option is not provided, the mirror_root_directory is scanned
# completely as usual
# mirror_subset_archives: /home/storage/missing-archives

# Randomize blocks of messages and send for consumption
block_messages: 250
```

### Run

Trigger the message computations:

```Shell
python3 -m swh.loader.tar.producer --config ~/.swh/producer/tar.yml
```

This will walk the `mirror_root_directory` folder and send encountered
tarball messages for the swh-loader-tar to uncompress (through
celery).

If the `mirror_subset_archives` is provided, the tarball messages will
be computed from such file (the `mirror_root_directory` is still used
so please be consistent).

If problem arises during tarball message computation, a message will
be output with the tarball that present a problem.

It will displayed the number of tarball messages sent at the end.

### Dry run

``` Shell
python3 -m swh.loader.tar.producer --config-file ~/.swh/producer/tar.yml --dry-run
```

This will do the same as previously described but only display the
number of potential tarball messages computed.

### Help

``` Shell
python3 -m swh.loader.tar.producer --help
```
