#!/usr/bin/env python3

# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import argparse
import sys

from swh.core import config
from swh.loader.tar import build, file


task_queue = 'swh.loader.tar.tasks.LoadTarRepository'


def compute_message_from(app, conf, root_dir, tarpath, filename,
                         retrieval_date, dry_run=False):
    """Compute and post the message to worker for the archive tarpath.

    Args:
        app: instance of the celery app
        conf: dictionary holding static metadata
        root_dir: root directory
        tarball: the archive's representation
        retrieval_date: retrieval date of information
        dry_run: will compute but not send messages

    Returns:
        None

    """
    origin = build.compute_origin(conf['url_scheme'],
                                  conf['type'],
                                  root_dir,
                                  tarpath)
    revision = build.compute_revision(tarpath)
    occurrence = build.occurrence_with_date(retrieval_date, tarpath)

    if not dry_run:
        app.tasks[task_queue].delay(tarpath,
                                    origin,
                                    revision,
                                    [occurrence])


def produce_archive_messages_from(app, conf, path,
                                  retrieval_date,
                                  mirror_file=None,
                                  dry_run=False):
    """From path, produce archive tarball messages to celery.

    Will print error message when some computation arise on archive
    and continue.

    Args:
        app: instance of the celery app
        conf: dictionary holding static metadata
        path: top directory to list archives from.
        retrieval_date: retrieval date of information
        mirror_file: a filtering file of tarballs to load
        dry_run: will compute but not send messages

    Returns:
        None

    Raises:
        None

    """

    limit = conf['limit']
    block = int(conf['block_messages'])
    count = 0

    path_source_tarballs = mirror_file if mirror_file else path

    for tarpath, fname in file.random_archives_from(path_source_tarballs,
                                                    block,
                                                    limit):
        try:
            compute_message_from(app, conf, path, tarpath, fname,
                                 retrieval_date, dry_run)
            count += 1
        except ValueError:
            print('Problem with the following archive: %s' % tarpath)

    return count


def load_config(conf_file):
    """Load the configuration from file.

    Args:
        conf_file: path to a configuration file with the following content:
        [main]

        # mirror's root directory holding tarballs to load into swh
        mirror_root_directory = /home/storage/space/mirrors/gnu.org/gnu/

        # origin setup's possible scheme url
        url_scheme = rsync://ftp.gnu.org/gnu/

        # origin type used for those tarballs
        type = ftp

        # For tryouts purposes (no limit if not specified)
        limit = 1

    Returns:
        dictionary of data present in the configuration file.


    """
    conf = config.read(conf_file,
                       default_conf={'limit': ('int', None)})
    url_scheme = conf['url_scheme']
    mirror_dir = conf['mirror_root_directory']

    # remove trailing / in configuration (to ease ulterior computation)
    if url_scheme[-1] == '/':
        conf.update({
            'url_scheme': url_scheme[0:-1]
        })

    if mirror_dir[-1] == '/':
        conf.update({
            'mirror_root_directory': mirror_dir[0:-1]
        })

    return conf


def parse_args():
    """Parse the configuration from the cli.

    """
    cli = argparse.ArgumentParser(
        description='Tarball producer of local fs tarballs.')
    cli.add_argument('--dry-run', '-n',
                     action='store_true',
                     help='Dry run (print repo only)')
    cli.add_argument('--config', '-c', help='configuration file path')

    args = cli.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()
    config_file = args.config
    if not config_file:
        print('Missing configuration file option.')
        sys.exit(1)

    # instantiate celery app with its configuration
    from swh.scheduler.celery_backend.config import app
    from swh.loader.tar import tasks  # noqa

    conf = load_config(config_file)

    retrieval_date = conf['date']

    nb_tarballs = produce_archive_messages_from(
        app,
        conf,
        conf['mirror_root_directory'],
        retrieval_date,
        conf.get('mirror_subset_archives'),
        args.dry_run)

    print('%s tarball(s) sent to worker.' % nb_tarballs)
