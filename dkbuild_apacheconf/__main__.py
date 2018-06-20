# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import sys
import textwrap
from jinja2 import Template
from dkfileutils.path import Path

from dkbuild_apacheconf.context import Context
from . import __version__, __doc__ as module_doc
import argparse


DIRNAME = Path(__file__).dirname()
APACHECONF_TEMPLATE = DIRNAME / 'apache.conf.jinja'


def init_cmd(argv, args):
    site_ini = Path('site.ini')
    if site_ini.exists() and not args.force:
        print(textwrap.dedent("""
            ERROR: site.ini exists
        """),  file=sys.stderr)
        sys.exit(1)
    else:
        site_ini.write(DIRNAME / 'site.ini')
        if args.verbose:
            print((DIRNAME / 'site.ini').read())


def run_cmd(argv, args):
    ctx = Context(argv, args)
    t = Template(APACHECONF_TEMPLATE.read())
    txt = ctx.render(t)
    if args.dry:
        print(txt)
    else:
        apache_conf = Path(args.out)
        apache_conf.write(txt)


def main():
    p = argparse.ArgumentParser(description=module_doc)
    p.add_argument('-V', '--version', action='version', version="%(prog)s v" + __version__)
    p.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity')
    p.add_argument('-f', '--force', action='store_true', help='force operation')
    p.add_argument('--dry', action='store_true', help="don't write to disk")
    p.add_argument('-i', '--site', metavar='FILE',
                   help='site.ini input file', default='site.ini')
    p.add_argument('-o', '--out', metavar='FILE',
                   help='output filename (default apache.conf)', default='apache.conf')
    p.add_argument('-s', '--server', metavar='FILE',
                   help='server.ini file to use (default apache.conf)', default='server.ini')
    p.add_argument('--skip-server', action='store_true', help="don't look for server.ini file.")
    p.add_argument('command', nargs='?', help="run command")

    args, argv = p.parse_known_args()

    if args.verbose:
        print(args, argv)

    if args.command:
        globals()[args.command + '_cmd'](argv, args)

    sys.exit(0)


if __name__ == "__main__":
    main()
