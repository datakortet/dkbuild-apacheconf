# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import textwrap

from dkfileutils.path import Path
from jinja2 import Template

from dkbuild_apacheconf.context import Context

DIRNAME = Path(__file__).dirname()
APACHECONF_TEMPLATE = DIRNAME / 'apache.conf.jinja'
SITE_INI_TEMPLATE = DIRNAME / 'site.ini'


def init_cmd(argv, args):
    site_ini = Path('site.ini')
    if site_ini.exists() and not args.force:
        print(textwrap.dedent("""
            ERROR: site.ini exists, writing to site.ini.new
        """),  file=sys.stderr)
        site_ini = Path('site.ini.new')

    site_ini.write(SITE_INI_TEMPLATE.read())
    if args.verbose or True:
        print(SITE_INI_TEMPLATE.read())


def run_cmd(argv, args):
    """Create a new apache.conf file from site.ini and server.ini
    """
    ctx = Context(argv, args)
    template_text = APACHECONF_TEMPLATE.read()
    t = Template(template_text)
    txt = ctx.render(t)
    # print('start')
    # print(txt)
    # print('end')
    if args.dry:
        print(txt)
    else:
        with open(args.out, 'wb') as fp:
            fp.write(txt.encode('u8').replace(b'\r\n', b'\n'))
        # apache_conf = Path(args.out)
        # apache_conf.write(txt.replace('\r\n', '\n'))
