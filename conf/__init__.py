
from pony import orm

from k2.utils.autocfg import AutoCFG

try:
    from .private import aeon
except ImportError:
    aeon = {}

try:
    from .private import db
except ImportError:
    db = {}

try:
    from .private import rank
except ImportError:
    rank = {}

try:
    from .private import api
except ImportError:
    api = {}

try:
    from .private import graph
except ImportError:
    graph = {}

conf = AutoCFG(
    {
        'aeon': AutoCFG(aeon).update_missing(
            {
                'use_ssl': False,
                'port': 8080,
                'https_port': 8081,
                'host': '',
                'ssl': None,
                'ssl_handshake_timeout': None,
                'site_dir': './var/',
                'pws_secret': 'pws_secret',
                'request': {
                    'request_header': 'x-user-id',
                    'protocol': {
                        'allowed_methods': {'GET', 'POST'},
                    }
                },
            },
        ),
        'db': AutoCFG(db).update_missing(
            {
                'provider': 'mysql',
                'host': None,
                'port': None,
                'user': None,
                'passwd': None,
                'db': None,
            },
        ),
        'rank': AutoCFG(rank).update_missing(
            {
                'quality_precision': 1000.0,
                'proc_num': 4,
            },
        ),
        'graph': AutoCFG(graph).update_missing(
            {
                'file': 'graph.dump',
                'proc_num': 4,
            },
        ),
        'node2vec': AutoCFG(graph).update_missing(
            {
                'model_filename': 'model.n2v',
                'embeding_filename': 'embed.n2v',
                'edges_filename': 'edges.n2v',
            }
        ),
        'api': AutoCFG(api).update_missing(
            {
                'secret': '0123456789',
                'cache_dump_enable': True,
                'cache_dump_file': 'cache.dump',
            },
        ),
    }
)

conf.sql = orm.Database(**conf.db)
