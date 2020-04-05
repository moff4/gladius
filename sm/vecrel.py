
from k2.aeon.sitemodules import (
    AuthSM,
    RestSM,
)

from conf import conf
from logic import Cursach


ALG_MAP = {
    'mindminer': {
        'func': (cursach := Cursach()).relevanse,
        'params': {},
    },
    'rankedminer': {
        'func': cursach.ranked_relevanse,
        'params': {},
    }
}


class VecRelSM(AuthSM, RestSM):

    POST_schema = {
        'type': dict,
        'value': {
            'alg': {
                'type': 'const',
                'value': set(ALG_MAP)
            },
            'cases': {
                'type': dict,
                'anykey': {
                    'type': dict,
                    'value': {
                        'user': {'type': list, 'value': str},
                        'target': {'type': list, 'value': str},
                        'params': {'type': dict, 'default': dict},
                    },
                },
            },
        },
    }

    @staticmethod
    def authorizator(request):
        return request.headers.get('x-api-secret') == conf.api.secret

    @staticmethod
    def get(request):
        return {
            'result': [
                {
                    'name': alg_name,
                    'params': alg_data['params'],
                }
                for alg_name, alg_data in ALG_MAP.items()
            ]
        }

    async def post(self, request):
        return {
            'result': await ALG_MAP[request.data['alg']]['func'](request.data['cases'])
        }
