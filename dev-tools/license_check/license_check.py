#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import argparse
import shutil
import os
import re
import tempfile
import datetime

from StringIO import StringIO

LICENSE_FILE_PATH = 'gpl3.txt'

LICENSE_FILE_NAME = 'LICENSE'

ENCODING_LINE = '# -*- coding: utf-8 -*-'
ENCODING_REGEX = re.compile(r'^# -\*- coding:(.*)-\*-')

VARIABLE_LICENSE_REGEX = re.compile(r'__license__ += +("+)(.*?)(\1)\n', re.S)

COPYRIGHT_REGEX = re.compile(r'^#? *Copyright +\((C|c)\) (\d{4})( ?- ?(\d{4}))?', re.M)
LICENSE_HEADER = """# Copyright (C) %(year)s Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

def add_license_file(repopath):
    licensepath = os.path.join(repopath, LICENSE_FILE_NAME)
    if not os.path.exists(licensepath):
        shutil.copyfile(LICENSE_FILE_PATH, licensepath)

def find_all_python_files(repopath, exclude):
    python_files = []
    for path, dirs, files in os.walk(repopath):
        for filename in files:
            if filename.endswith(".py") and filename not in exclude:
                python_files.append(os.path.join(path, filename))
    return python_files

def add_headers(filepath):
    with open(filepath) as pyfile:
        contents = pyfile.read()

    contents = contents.lstrip()

    contents, shebang = chop_shebang(contents)

    contents = remove_encoding(contents)

    contents, copyright = chop_copyright(contents)

    year = revise_copyright_year(copyright)

    contents = contents.lstrip()

    tmpfile = file_with_headers(contents, year, shebang)

    with open(filepath, 'w') as pyfile:
        pyfile.write(tmpfile.read())

    tmpfile.close()

def remove_encoding(contents):
    contents = contents.lstrip()
    contents = ENCODING_REGEX.sub("", contents, count=1)
    contents = contents.lstrip()
    return contents

def chop_shebang(contents):
    contents = contents.lstrip()
    if contents.startswith("#!"):
        shebang, _, contents = contents.partition("\n")
        return contents, shebang

    return contents, None

def chop_copyright(contents):
    contents = contents.lstrip()
    contents, copyright = chop_commented_license(contents)

    if not copyright:
        contents, copyright = chop_variable_license(contents)

    return contents, copyright

def chop_commented_license(contents):
    reader = StringIO(contents)

    comments = []
    line = reader.readline()
    while line and line.startswith('#'):
        comments.append(line)
        line = reader.readline()

    if has_copyright(comments):
        pos = reader.tell() - len(line)
        copyright = contents[0:pos].strip()
        contents = contents[pos:].lstrip()
        return contents, copyright

    return contents, None

def chop_variable_license(contents):
    contents = contents.lstrip()

    match = VARIABLE_LICENSE_REGEX.search(contents)
    if match:
        license = match.group(2)
        contents = VARIABLE_LICENSE_REGEX.sub("", contents, count=1).lstrip()
        return contents, license

    return contents, None

def revise_copyright_year(copyright=None):
    current_year = datetime.datetime.now().year
    if not copyright:
        return str(current_year)

    years = set([current_year])

    for match in COPYRIGHT_REGEX.finditer(copyright):
        years.add(int(match.group(2)))
        if match.group(4):
            years.add(int(match.group(4)))

    min_year = min(years)
    max_year = max(years)

    if min_year == max_year:
        return str(min_year)
    else:
        return "%s-%s" % (min_year, max_year)

def file_with_headers(contents, year, shebang=None):
    tmpfile = tempfile.TemporaryFile()

    if shebang:
        tmpfile.write('%s\n' % shebang)

    tmpfile.write('%s\n\n' % ENCODING_LINE)
    tmpfile.write(LICENSE_HEADER % {'year': year})
    tmpfile.write('\n')
    tmpfile.write(contents)
    tmpfile.seek(0)

    return tmpfile

def has_copyright(lines):
    for line in lines:
        if COPYRIGHT_REGEX.match(line):
            return True
    return False

def read_filelist(path):
    with open(path) as reader:
        elements = [l.strip() for l in reader]
    return elements

if __name__ == "__main__":

    parser = argparse.ArgumentParser('add GPL license to project repo and file headers')
    parser.add_argument('projectroot', help='folder containing all the projects')
    parser.add_argument('-L', '--no-license', action='store_false', dest='license',
            default=True, help='do not copy license file')
    parser.add_argument('-H', '--no-header', action='store_false', dest='header',
            default=True, help='do not insert license in header')
    parser.add_argument('-r', '--repos', default='repos.txt',
            help='text file with a list of repositories to scan (default: repos.txt)')
    parser.add_argument('-e', '--exclude', default='exclude.txt',
            help='text file with a list of python files to exlude  (default: exclude.txt)')

    args = parser.parse_args()

    root = args.projectroot
    repos = read_filelist(args.repos)
    exclude = read_filelist(args.exclude)

    for repo in repos:
        repopath = os.path.join(root, repo)

        if args.license:
            print "adding license file in", repopath
            add_license_file(repopath)

        if args.header:
            files = find_all_python_files(repopath, exclude)
            for filepath in files:
                print "processing", filepath
                add_headers(filepath)