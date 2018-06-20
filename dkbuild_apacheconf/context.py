# -*- coding: utf-8 -*-
from __future__ import print_function
import copy
import json
import re
import sys
# noinspection PyCompatibility
import configparser
import ast
from dkfileutils.path import Path
from collections import defaultdict

from . import mergesettings
from .errors import NoServerIniError
from .defaults import DEFAULTS


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
    cp = configparser.RawConfigParser()
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


def read_settings_files(argv, args):
    try:
        if args.skip_server:
            site_ini = read_ini(args.site)
        else:
            site_ini = read_ini([args.site, find_server_ini(argv, args)])
        return site_ini
    except NoServerIniError:
        print("Couldn't find a server.ini file anywhere in the parents to "
              "site.ini.", file=sys.stderr)
        sys.exit(1)


class Context(object):
    def __init__(self, argv, args):
        self._ctx = {}
        self._flatcache = {}
        self._fetch_context(argv, args)

    def render(self, template):
        return template.render(**self._ctx)

    def _fetch_context(self, argv, args):
        defaults = copy.deepcopy(DEFAULTS)
        settings = read_settings_files(argv, args)

        self._ctx = mergesettings.merge(defaults, settings)
        if args.verbose:
            print("CTX", json.dumps(self._ctx, indent=4))
