
# check context.py for derived settings

DEFAULTS = {
    'server': {
        'admin': 'bp@norsktest.no',  # FIXME
        # 'admin': 'bp@datakortet.no',  # FIXME
        'apache_version': 24,
    },
    'site': {
        'ports': [80],
        'dns': 'www.domain-name.com',
        'sitename': 'sitename',
        'virtual_env': 'virtual_env',
        'www_prefix': None,
        'block_request_methods': "TRACE|TRACK|OPTIONS|PROPFIND",

    },
    'wsgi': {
        'processes': None,
    }
}
