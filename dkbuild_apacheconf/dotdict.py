# -*- coding: utf-8 -*-
from __future__ import print_function
import json

from past import builtins

class dotdict(object):
    def __init__(self):
        self.ctx = {}

    def __repr__(self):
        return '<dotdict %s>' % json.dumps(self._flatten(), indent=4, sort_keys=True)

    def __str__(self):
        return '<dotdict %s>' % json.dumps(self.ctx, indent=4, sort_keys=True)

    def _traverse(self, key):
        cur = self.ctx
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

    def __setitem__(self, key, value):
        if not isinstance(key, builtins.basestring):
            raise TypeError("keys must be strings")

        cur = self.ctx
        parts = key.split('.')
        for part in parts[:-1]:
            if part not in cur:
                cur[part] = {}
            cur = cur[part]
        cur[parts[-1]] = value

    def __contains__(self, key):
        p, k, v = self._traverse(key)
        return k in p

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

        _do_flatten('', self.ctx)
        return _flat
