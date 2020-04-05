import math
import asyncio
from pony import orm
from multiprocessing.pool import Pool

from k2.logger import new_channel

from conf import conf
from db import (
    Tag,
    PostTag,
)
from logic import ranks
from utils import parse_args

logger = new_channel('ranks')

ARGS = {
    'dry': False,
    'tags': None,
    'limit': None,
    'reverse': None,
}

task_description = 'count ranks for tags; args: %s' % ', '.join(list(ARGS))


def parallel_post_ranks(args):
    return post_ranks(*args)


def post_ranks(post, weight_views, weight_likes, weight_reposts):
    rank_pop, rank_qual = ranks(
        post_date=post['post_date'],
        views=post['views'],
        likes=post['likes'],
        reposts=post['reposts'],
        _time=post['timestamp'],
        weight_views=weight_views,
        weight_likes=weight_likes,
        weight_reposts=weight_reposts,
    )
    return rank_pop, rank_qual


async def tag_ranks(tag: Tag, dry_mode: bool=False) -> (float, float):
    if tag.rank_pop is not None and tag.rank_qual is not None:
        return tag.rank_pop, tag.rank_qual
    p, q = 0.0, 0.0
    c = 0
    weight_views, weight_likes, weight_reposts = PostTag.rank_weights(tag.tag)
    pts = [
        {
            'post_date': pt.post.post_date,
            'views': pt.post.views,
            'likes': pt.post.likes,
            'reposts': pt.post.reposts,
            'timestamp': pt.post.timestamp,
        }
        for pt in tag.posts.filter(lambda p: p.post.from_group > 0)
    ]
    c = len(pts)

    proc_num = conf.rank.proc_num
    with Pool(proc_num) as pool:
        b = int(c / proc_num + 1)
        for _q, _p in pool.map(
            parallel_post_ranks,
            [
                (
                    pt,
                    weight_views,
                    weight_likes,
                    weight_reposts,
                )
                for i in range(proc_num)
                for pt in pts[b * i: b * (i + 1)]
            ]
        ):
            p += _q
            q += _q
    if c:
        p = math.log(1.0 + float(p) / float(c))
        q = math.log(1.0 + float(q) / float(c))
    else:
        p = 0.0
        q = 0.0
    if not dry_mode:
        tag.rank_pop = p
        tag.rank_qual = q
    await logger.debug(
        '"{}": p{:.4f} q{:.4f}',
        tag.tag,
        p,
        q,
    )
    return p, q


async def count_ranks(qs, dry_mode):
    x = 0
    try:
        for tag in qs:
            await tag_ranks(tag, dry_mode)
            x += 1
            if not dry_mode and not (x % 100):
                orm.commit()
    except Exception:
        await logger.exception('T.ranks counted:')
    finally:
        return x


async def count_all(qs, dry_mode):
    done, count = 0, qs.count()
    while done < count:
        done += await count_ranks(
            qs=qs.limit(100),
            dry_mode=dry_mode,
        ) or 1


@orm.db_session
def start():
    args = parse_args(ARGS)
    qs = orm.select(
        t
        for t in Tag
        if t.checked is not None
        if t.rank_pop is None or t.rank_qual is None
    )
    if args['tags']:
        qs = qs.filter(lambda t: t.tag in args['tags'].split(','))
    if args['reverse']:
        qs = qs.order_by(lambda t: orm.desc(t.tag))
    if args['limit']:
        qs = qs.limit(int(args['limit']))
        coro = count_ranks(qs=qs, dry_mode=args['dry'])
    elif args['tags'] is None:
        coro = count_all(qs=qs, dry_mode=args['dry'])
    else:
        coro = count_ranks(qs=qs, dry_mode=args['dry'])

    try:
        asyncio.run(coro)
    except KeyboardInterrupt:
        ...
