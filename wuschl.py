#!/usr/bin/env python2

import errno
import os
import subprocess
import sys
import jinja2

base_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_path, 'templates')
template_loader = jinja2.FileSystemLoader(template_path)
template_env = jinja2.Environment(loader=template_loader)

class Fuzzy(object):
    def __init__(self, name):
        self.name = name
        self.afldir = name + '_afl'
        self.testcases = []

    def _load_testcases(self):
        pass

    def _dict(self):
        return dict([ (key, getattr(self, key)) for key in dir(self) if not key.startswith('_')
                                                           and not callable(getattr(self, key))])

    def _render(self, suffix, template):
        with open(self.name + suffix, 'w') as ofile:
            ofile.write(template_env.get_template(template).render(self._dict()))

    def _collect(self):
        def _to_bin(binary):
            return ''.join([ '\\x%02x' % ord(b) for b in binary])

        self.testcases = []
        if not os.path.exists(self.afldir + '/queue'):
            return

        subprocess.check_call(['afl-cmin', '-i', self.afldir + '/queue', '-o', self.afldir + '/queue-min',
                               '--', './%s' % self.name, '-r'])

        for f in os.listdir(self.afldir + '/queue-min'):
            with open(os.path.join(self.afldir, 'queue-min', f), 'rb') as input_file:
                input_data = input_file.read()
            p = subprocess.Popen(['./%s' % self.name, '-r'], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_data,_ = p.communicate(input_data)
            p.wait()
            ret = p.returncode
            self.testcases.append({
                'input': _to_bin(input_data),
                'input_len': len(input_data),
                'output': _to_bin(output_data),
                'output_len': len(output_data),
                'ret': ret
            })

    def create(self):
        self._render('.c', 'main.c.j2'),
        self.update()
        return 0

    def update(self):
        self._collect()
        self._render('_tests.h', 'test.h.j2')
        return 0

    def fuzz(self):
        inputdir = self.afldir + '/input'
        for d in self.afldir, inputdir:
            try:
                os.mkdir(d)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.listdir(inputdir):
            print >>sys.stderr, "Please create one or more input files and put them into %s" % inputdir
            return 1
        os.execvp("afl-fuzz", ["afl-fuzz", "-i", inputdir, "-o", self.afldir, "--",
                               "./%s" % self.name, "-r"])
        return 1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: %s <name> <op>" % (sys.argv[0])
        sys.exit(1)
    f = Fuzzy(sys.argv[1])
    op = getattr(f, sys.argv[2], None)
    if not callable(op):
        print >>sys.stderr, "Unknown operation %r" % sys.argv[2]
        sys.exit(1)
    sys.exit(op())
