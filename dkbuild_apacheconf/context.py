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
        self._fetch_context(argv, args)
        # self._flatcache = self._flatten()
        self._derived_context(argv, args)
        if args.verbose:
            print(repr(self))
            print(str(self))
            # print("CTX", json.dumps(self._ctx, indent=4))

    def __repr__(self):
        return '<CTX %s>' % json.dumps(self._flatten(), indent=4, sort_keys=True)

    def __str__(self):
        cleanctx = {k: v for k, v in self._ctx.items() if not (k.startswith('run-once') or k.endswith('executable'))}
        return '<CTX %s>' % json.dumps(cleanctx, indent=4, sort_keys=True)

    def render(self, template):
        # return prettify_conf(template.render(**self._flatcache))
        return prettify_conf(template.render(**self._ctx))

    def _derived_context(self, argv, args):
        self['site_root'] = '${SRV}/www/' + self['site.sitename']
        self['django'] = self.get('site.django', 'yes')
        self['site.allow_trace'] = self.get('site.allow_trace', False)
        self['docroot'] = self.get('site.docroot', self['site_root'] + '/docroot')
        self['docroot_opts'] = self.get('docroot_opts', {})
        self['server_admin'] = self.get('server.admin')
        www_prefix = self['www_prefix'] = self.get('site.www_prefix', 'omit')

        self['redirect_to_https'] = False
        if 'site.https' in self:
            self['use_https'] = True
            if self['site.https'] in (True, 'only'):
                self['ports'] = [443, 80]
            if self['site.https'] == 'only':
                self['redirect_to_https'] = True
        else:
            self['use_https'] = False
            self['ports'] = [80]

        dns = self['site.dns']
        if dns.startswith('www.'):
            dns = dns[4:]
        self['dns'] = dns
        self['site.dns'] = dns
        self['fqdns'] = ('www.' if www_prefix else '') + dns


    def _fetch_context(self, argv, args):
        defaults = copy.deepcopy(DEFAULTS)
        settings = read_settings_files(argv, args)
        self._ctx = mergesettings.merge(defaults, settings)

    def _traverse(self, key):
        cur = self._ctx
        parts = key.split('.')
        for part in parts[:-1]:
            if part in cur:
                cur = cur[part]
        return cur, parts[-1], cur.get(parts[-1])  # parent, key, value

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def __getitem__(self, key):
        p, k, v = self._traverse(key)
        return v
        # return self._flatcache[key]

    def __setitem__(self, key, value):
        p, k, v = self._traverse(key)
        p[k] = value
        # self._flatcache[key] = value

    def __contains__(self, key):
        p, k, v = self._traverse(key)
        return k in p
        # return key in self._flatcache

    def _flatten(self):
        _flat = {}

        def _key(c, k):
            return k if not c else c + '.' + k

        def _do_flatten(curkey, item):
            for k, v in item.items():
                if isinstance(v, dict):
                    _do_flatten(_key(curkey, k), v)
                else:
                    _flat[_key(curkey, k)] = v

        _do_flatten('', self._ctx)
        return {k: v for k, v in _flat.items() if not (k.startswith('run-once') or k.endswith('executable'))}
