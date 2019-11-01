# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import textwrap

from dkfileutils.path import Path
from jinja2 import Template

from dkbuild_apacheconf.context import Context

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
    """Create a new apache.conf file from site.ini and server.ini
    """
    ctx = Context(argv, args)
    t = Template(APACHECONF_TEMPLATE.read())
    txt = ctx.render(t)
    if args.dry:
        print(txt)
    else:
        with open(args.out, 'wb') as fp:
            fp.write(txt.encode('u8').replace(b'\r\n', b'\n'))
        # apache_conf = Path(args.out)
        # apache_conf.write(txt.replace('\r\n', '\n'))
