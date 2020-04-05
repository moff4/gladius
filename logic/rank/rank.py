#!/user/bin/env python3
import math
import time

from conf import conf

from .wr import (
    interpolice,
    WeightRandom,
    WR_params,
)

LOOPS_MAP = {}

for i in range(10):
    LOOPS_MAP[i] = 50
for i in range(10, 50):
    LOOPS_MAP[i] = 10
for i in range(50, 100):
    LOOPS_MAP[i] = 5


def f(_time) -> float:
    tt = time.localtime(_time)
    return interpolice((float(tt.tm_hour) + (float(tt.tm_min) / 60.0))) + 1


def mark_rank(j, w, post_date, wr) -> float:
    _k = LOOPS_MAP.get(j, 1)
    return w / sum(
        (1.0 + f(post_date + sum(wr.random(_k)) / float(_k)))
        for _ in range(j)
    )


def ranks(
        post_date: int,
        likes: int,
        reposts: int,
        views: int,
        _time: int,
        weight_views: float,
        weight_likes: float,
        weight_reposts: float,
) -> tuple:
    """
        count rank for post
        :rtype tuple: (rank_pop as float, rank_qual as float)
    """
    def will_be(x):
        if (x > 0) and (
            y := int(
                wr.will_be(
                    count_now=x,
                    now=_time,
                )
            )
        ) > 0:
            return y
        return x
    wr = WeightRandom(WR_params(post_date, f(post_date)))

    views = will_be(views)

    rank_qual = sum(
        mark_rank(j, w, post_date, wr)
        for j, w in [
            (will_be(likes), weight_likes),
            (will_be(reposts), weight_reposts),
        ]
        if j
    )
    rank_pop = rank_qual
    if views:
        rank_qual /= views / conf.rank.quality_precision
        rank_qual = math.log(rank_qual + 1.0)
    else:
        rank_qual = 0.0
    rank_pop = math.log(rank_pop + 1.0)
    if views:
        rank_pop += mark_rank(views, weight_views, post_date, wr)
    wr.destruct()
    return rank_pop, rank_qual
