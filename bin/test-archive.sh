#!/usr/bin/env bash

generated_ar=./emacs-19.34.6-src.tar.gz
original_ar=/home/storage/space/mirrors/gnu.org/old-gnu/emacs/windows/19.34/src/emacs-19.34.6-src.tar.gz

tmpdir=$(mktemp -d)
tmpdirgnu=$(mktemp -d)

tar xvf $generated_ar -C $tmpdir
tar xvf $original_ar -C $tmpdirgnu

echo "diff -r ar:$tmpdir gnu:$tmpdirgnu"
diff -r $tmpdir $tmpdirgnu


rm -rf $tmpdir $tmpdirgnu
