# -*- coding: utf-8 -*-
from __future__ import print_function

import ConfigParser
import ast
import copy
import json
import os
import re
import sys
import textwrap
from collections import defaultdict

from jinja2 import Template

from dkfileutils.path import Path
from . import __version__, __doc__ as module_doc
from .defaults import DEFAULTS
import argparse


DIRNAME = Path(__file__).dirname()
APACHECONF_TEMPLATE = DIRNAME / 'apache.conf.jinja'

class NoServerIniError(Exception):
    pass

class YamlReaderError(Exception):
    pass

def data_merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, (dict, defaultdict)):
            # dicts must be merged
            if isinstance(b, (dict, defaultdict)):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError, e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


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


def prettify_conf(txt):
    lines = [line.rstrip() for line in txt.split('\n')]
    txt = '\n'.join(lines)
    return re.sub(r'\n\n+', '\n\n', txt)


def find_server_ini(argv, args):
    site_ini = Path(args.site)
    for pth in site_ini.parents:
        if args.server in pth.listdir():
            return pth / args.server
    raise NoServerIniError("%s not found." % args.server)


def read_ini(fnames):
    cp = ConfigParser.RawConfigParser()
    cp.read(fnames)
    res = defaultdict(dict)
    for section in cp.sections():
        for opt in cp.options(section):
            val = cp.get(section, opt)
            try:
                val =  ast.literal_eval(val)
            except (ValueError, SyntaxError):
                if val.lower() in ('yes', 'y'):
                    val = True
                elif val.lower() in ('no', 'n'):
                    val = False
            res[section][opt] = val
            # res['%s.%s' % (section, opt)] = cp.get(section, opt)
    return res


def fetch_context(argv, args):
    ctx = copy.deepcopy(DEFAULTS)
    try:
        if args.skip_server:
            site_ini = read_ini(args.site)
        else:
            site_ini = read_ini([args.site, find_server_ini(argv, args)])
        ctx.update(site_ini)
        data_merge(ctx, site_ini)
        if args.verbose:
            print("CTX", json.dumps(ctx, indent=4))
        return ctx
    except NoServerIniError:
        print("Couldn't find a server.ini file anywhere in the parents to " \
              "site.ini.", file=sys.stderr)
        sys.exit(1)


def run_cmd(argv, args):
    t = Template(APACHECONF_TEMPLATE.read())
    res = t.render(**fetch_context(argv, args))
    txt = prettify_conf(res)
    print(txt)
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
