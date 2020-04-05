import asyncio
from pony import orm

from k2.logger import new_channel

from conf import conf
from db import TagTagMap

logger = new_channel('graph-dump')
task_description = 'dump graph to file (for clustering & pather)'


async def dump():
    done = 0
    try:
        with orm.db_session:
            await logger.info('gonna dump graph into file "{}"', conf.graph.file)
            with open(conf.graph.file, 'w') as f:
                for row in orm.select(tag for tag in TagTagMap):
                    f.write('{} {} {}\n'.format(row.tag1.tag, row.tag2.tag, 1.0 / row.posts_num))
                    done += 1
                    if not (done % 1000):
                        await logger.debug('dumped {} rows', done)
    except Exception as ex:
        await logger.error('got exception: {}', ex)
    else:
        await logger.info('success!')


def start():
    asyncio.run(dump())
