from __future__ import print_function

import sys
import os
import subprocess
import time
try:
    from StringIO import StringIO  # Python2
except ImportError:
    from io import StringIO  # Python3


PY2 = sys.version_info < (3,)
PY3 = sys.version_info > (3,)

TMP_SED = 'tmp.sed'
TMP_INPUT = 'tmp.input'
TMP_PY = 'tmp.py'


class NumsedConversion:
    def __init__(self, source, transformation):
        self.source = source
        self.transformation = transformation

    def trace(self):
        return ''

    def run(self, verbose=True):
        return ''

    def coverage(self):
        return 'Coverage not implemented for current conversion.'


class ListStream:
    def __enter__(self):
        self.result = StringIO()
        sys.stdout = self.result
        return self
    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__
    def stringlist(self):
        return self.result.getvalue().splitlines()
    def singlestring(self):
        return self.result.getvalue()


def run(cmd, echo=True):
    try:
        p = subprocess.Popen(cmd.split(),
                            #shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    except:
        print('Unable to start', cmd)
        exit(1)

    res = []
    while True:
        line = p.stdout.readline()
        line = line.decode('ascii') # py3
        if line == '':
            break
        else:
            line = line.rstrip('\n\r')
            res.append(line)
            if echo:
                print(line)
    return '\n'.join(res)


def testlines(name):
    '''
    yield each test in a test suite

    Tests are made of a script section and an optional result section when
    numsed result is different from python result. Tests are separated with
    comments including '---'. Optional results are introduced with comments
    including '==='.
    Returns the lines of the script and the optional result (None when absent).
    '''
    script_lines = []
    result_lines = None
    dest = script_lines
    with open(name) as f:
        for line in f:
            if line.startswith('#') and '---' in line:
                yield script_lines, result_lines
                script_lines = []
                result_lines = None
                dest = script_lines
            elif line.startswith('#') and '===' in line:
                result_lines = []
                dest = result_lines
            else:
                # append to script lines in script section, to result lines in
                # result setion
                dest.append(line)


def list_compare(tag1, tag2, list1, list2):
    # make sure both lists have same length
    maxlen = max(len(list1), len(list2))
    list1.extend([''] * (maxlen - len(list1)))
    list2.extend([''] * (maxlen - len(list2)))

    # with open('list1.txt', 'w') as f:
    #     for line in list1:
    #         print>>f, line
    # with open('list2.txt', 'w') as f:
    #     for line in list2:
    #         print>>f, line

    diff = list()
    res = True
    for i, (x, y) in enumerate(zip(list1, list2)):
        if x != y:
            diff.append('line %s %d: %s' % (tag1, i + 1, x))
            diff.append('line %s %d: %s' % (tag2, i + 1, y))
            res = False
    return res, diff


def hasextension(filename, *ext):
    return os.path.splitext(filename)[1].lower() in [_.lower() for _ in ext]
