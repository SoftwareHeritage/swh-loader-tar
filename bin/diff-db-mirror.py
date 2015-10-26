#!/usr/bin/env python3

# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import argparse
import os
import psycopg2
import sys

from swh.loader.tar import tarball


def connect(db_url):
    """Open db connection.
    """
    return psycopg2.connect(db_url)


def execute(cur, query_params):
    """Execute the query_params.
    query_params is expected to be either:
    - a sql query (string)
    - a tuple (sql query, params)
    """
    if isinstance(query_params, str):
        cur.execute(query_params)
    else:
        cur.execute(*query_params)


def query_fetch(db_conn, query_params):
    """Execute sql query which returns results.
    query_params is expected to be either:
    - a sql query (string)
    - a tuple (sql query, params)
    """
    with db_conn.cursor() as cur:
        execute(cur, query_params)
        yield from cursor_to_bytes(cur)


def entry_to_bytes(entry):
    """Convert an entry coming from the database to bytes"""
    if isinstance(entry, memoryview):
        return entry.tobytes()
    return entry


def line_to_bytes(line):
    """Convert a line coming from the database to bytes"""
    return line.__class__(entry_to_bytes(entry) for entry in line)


def cursor_to_bytes(cursor):
    """Yield all the data from a cursor as bytes"""
    yield from (line_to_bytes(line) for line in cursor)


def list_branches(db_url):
    """Return the distinct list of branches present in occurrence_history.

    """
    with connect(db_url) as db_conn:
        for branch in query_fetch(db_conn,
                                  'select distinct branch from '
                                  'occurrence_history'):
            yield branch[0]


def diff_branch(root_dir, existing_set):
    """Walk the root_dir and for every tarball not in existing_set,
    yield its absolute path.

    """
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.exists(filepath):
                continue
            if not tarball.is_tarball(filepath):
                continue
            if filename in existing_set:
                continue

            yield filepath


def parse_args():
    """Parse the configuration from the cli.

    """
    cli = argparse.ArgumentParser(
        description='Diff between db and local fs mirror tarballs directory.')
    cli.add_argument('--db-url', '-d',
                     help='db-url string')
    cli.add_argument('--mirror-root-directory', '-m',
                     help='mirror root directory')

    args = cli.parse_args()
    if not args.db_url or not args.mirror_root_directory:
        print('Bad usage, cf. --help')
        sys.exit(1)

    return args


if __name__ == '__main__':
    args = parse_args()

    db_url = args.db_url

    already_present = set(list_branches(db_url))

    root_dir = args.mirror_root_directory
    for filepath in diff_branch(root_dir, already_present):
        print(filepath)
