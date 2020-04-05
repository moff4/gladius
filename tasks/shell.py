
import IPython
from pony import orm

task_description = 'run shell'


@orm.db_session
def start():
    IPython.embed()
