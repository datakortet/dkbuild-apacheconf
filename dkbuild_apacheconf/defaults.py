

DEFAULTS = {
    'server': {
        'admin': None,
        'apache_version': 24,
    },
    'site': {
        'ports': [80],
        'dns': 'www.domain-name.com',
        'sitename': 'sitename',
        'virtual_env': 'virtual_env',
        'www_prefix': None,

    },
    'wsgi': {
        'processes': 4,
    }
}
