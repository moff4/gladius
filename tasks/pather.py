import asyncio
import random
from pony import orm

import networkx as nx
from k2.logger import new_channel

from conf import conf
from logic import GRAPH
from db import Tag, Path
from utils import parse_args
from utils.parallel import parallel_run


ARGS = {
    'limit': None,
}

logger = new_channel('pather')
task_description = 'find random pathes to fill Pather Table; args: %s' % ', '.join(list(ARGS))


def procc_worker(q_in, q_out):
    graph = GRAPH.graph
    with orm.db_session:
        while (args := q_in.get()) is not None:
            src, dst = args
            try:
                q_out.put(nx.dijkstra_path(graph, src, dst))
            except Exception as e:
                q_out.put('build path: %s' % e)
    q_in.close()
    q_out.close()
    q_in.join_thread()
    q_out.join_thread()


async def generate_pathes(limit):
    async def read(res):
        def write(data, try_: int = 0):
            try:
                with orm.db_session:
                    for idx, tag in enumerate(data):
                        Path(src=data[0], dst=data[-1], tag=tag, pos=idx)
                    return None
            except Exception as e:
                if try_ < 3:
                    return write(res, try_ + 1)
                return str(e)
        if res:
            if isinstance(res, list):
                await logger.info('build path for "{}" -> "{}"', res[0], res[-1])
                if res := write(res):
                    await logger.error(res)
            else:
                await logger.error(res)

    with orm.db_session:
        tags = list(t.tag for t in orm.select(t for t in Tag if t.checked))
    await parallel_run(
        itr=[
            (
                random.choice(tags),
                random.choice(tags),
            )
            for _ in range(limit)
        ],
        worker=procc_worker,
        handler=read,
        proc_num=conf.graph.proc_num,
    )


def start():
    args = parse_args(ARGS)
    asyncio.run(
        generate_pathes(
            limit=int(args['limit']) if args['limit'] else None,
        )
    )
