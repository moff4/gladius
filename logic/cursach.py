from typing import Any, List, Dict
from pony import orm

from k2.logger import new_channel

from db import Tag
from .graph import GRAPH


class Cursach:

    def __init__(self):
        self.logger = new_channel('cursach')

    async def prepare(self, cases: Dict[str, Any]):
        await GRAPH.multi_weight(
            (src, dst)
            for _, data in cases.items()
            for src in data['user']
            if src in GRAPH
            for dst in data['target']
            if dst in GRAPH
        )

    async def relevanse_one(
        self,
        user: List[str],
        target: List[str],
        params: Dict[str, Any],
        rank_map: Dict[str, float] = None
    ):
        rank_map = rank_map or {}
        r = [
            GRAPH.weight(src, dst) * rank_map.get(src, 1.0) * rank_map.get(dst, 1.0)
            for src in user
            if src in GRAPH
            for dst in target
            if dst in GRAPH
        ]
        return (sum(r) / len(r)) if r else 0.0

    async def relevanse(self, cases: Dict[str, Any]):
        await self.prepare(cases)
        res = {
            key: await self.relevanse_one(user=data['user'], target=data['target'], params=data['params'])
            for key, data in cases.items()
        }
        GRAPH.save()
        return res

    async def ranked_relevanse(self, cases: Dict[str, Any]):
        await self.prepare(cases)
        tags = {
            tag
            for _, data in cases.items()
            for pool_key in ['user', 'target']
            for tag in data[pool_key]
        }
        with orm.db_session:
            rank_map = {
                tag.tag: tag.rank_pop
                for tag in Tag.select(lambda t: t.tag in tags)
            }
        res = {
            key: await self.relevanse_one(
                user=data['user'],
                target=data['target'],
                params=data['params'],
                rank_map=rank_map,
            )
            for key, data in cases.items()
        }
        GRAPH.save()
        return res
