import asyncio
from pony import orm

from k2.logger import new_channel

from conf import conf
from db import Tag
from logic import Clustering
from utils import parse_args
from utils.parallel import parallel_run


ARGS = {
    'dry': False,
    'limit': None,
    'tag': None,
    'reverse': None,
}

logger = new_channel('clustering')
task_description = 'count clustering coeff for tag; args: %s' % ', '.join(list(ARGS))


def procc_worker(q_in, q_out):
    cl = Clustering()
    with orm.db_session:
        while (tag := q_in.get()) is not None:
            q_out.put((tag, cl.clustering_coeff(tag)))
    q_in.close()
    q_out.close()
    q_in.join_thread()
    q_out.join_thread()


async def count_clustering(tag: str, limit: int, dry_mode: bool, reverse: bool):
    async def read(t, c):
        nonlocal done
        done += 1
        await logger.info('clustering_coeff for "%s" is %s' % (t, c))
        if not dry_mode:
            Tag.get(lambda y: y.tag == t).clustering = c
            if not (done % 100):
                orm.commit()

    if tag:
        qs = orm.select(t for t in Tag if t.tag == tag)
    else:
        qs = orm.select(t for t in Tag if t.checked and t.clustering is None)
    if reverse:
        qs = qs.order_by(lambda t: orm.desc(t.tag))
    if limit:
        qs = qs.limit(limit)
    with orm.db_session:
        tags = {t.tag: None for t in qs}

    done = 0
    with orm.db_session:
        await parallel_run(list(tags), read, conf.rank.proc_num)


def start():
    args = parse_args(ARGS)
    asyncio.run(
        count_clustering(
            limit=int(args['limit']) if args['limit'] else None,
            dry_mode=args['dry'],
            tag=args['tag'],
            reverse=args['reverse'],
        )
    )
