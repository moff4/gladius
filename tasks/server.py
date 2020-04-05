
from conf import conf

from k2.aeon import Aeon

from sm import (
    VecRelSM,
)

task_description = 'run web api'


def start():
    server = Aeon(
        namespace={
            r'^/relevance': {
                r'^/vecrel$': VecRelSM(),
            },
        },
        **conf.aeon
    )
    server.run()
