import json
from typing import Iterable, Tuple, List

import networkx as nx
from k2.logger import new_channel

from conf import conf
from utils.parallel import parallel_run


def worker(q_in, q_out):
    graph = GRAPH.graph
    while (args := q_in.get()) is not None:
        src, dst = args
        try:
            q_out.put((src, dst, nx.dijkstra_path_length(graph, src, dst)))
        except Exception as e:
            q_out.put('build path: %s' % e)
    q_in.close()
    q_out.close()
    q_in.join_thread()
    q_out.join_thread()


class Graph:
    def __init__(self):
        self._graph = None
        self._loaded = False
        self.logger = new_channel('graph')
        self._cache_changed = False
        if conf.api.cache_dump_enable:
            try:
                self.cache = {
                    eval(key): value
                    for key, value in json.load(open(conf.api.cache_dump_file)).items()
                }
            except (IOError, json.JSONDecodeError):
                self.cache = dict()
        else:
            self.cache = dict()
            
    def __del__(self):
        self.save()

    def save(self):
        if conf.api.cache_dump_enable and self._cache_changed:
            try:
                data = json.dumps(
                    {
                        str(key): value
                        for key, value in self.cache.items()
                    }
                )
                with open(conf.api.cache_dump_file, 'w') as f:
                    f.write(data)
            except (IOError, json.JSONDecodeError):
                ...

    def load(self):
        if not self._loaded:
            self._graph = nx.read_weighted_edgelist(conf.graph.file)
            self._loaded = True

    async def handler(self, res):
        if isinstance(res, str):
            await self.logger.error(res)
        else:
            src, dst, w = res
            self.cache[self.key(src, dst)] = w
            self._cache_changed = True

    @staticmethod
    def key(src, dst):
        return (src, dst) if src > dst else (dst, src)

    @property
    def graph(self):
        self.load()
        return self._graph

    async def multi_weight(self, itr: Iterable[Tuple[str, str]]) -> None:
        if len(
            itr := list(
                {
                    key
                    for src, dst in itr
                    if src != dst
                    if (key := self.key(src, dst)) not in self.cache
                }
            )
        ) > 20:
            await self.logger.debug('gonna count weights for {} pairs', len(itr))
            await parallel_run(
                itr=itr,
                handler=self.handler,
                worker=worker,
                proc_num=conf.graph.proc_num,
            )
            await self.logger.debug('counted weights, cache - {}', len(self.cache))

    def weight(self, src: str, dst: str) -> float:
        if src == dst:
            return 0.0
        if (key := self.key(src, dst)) not in self.cache:
            self.cache[key] = nx.dijkstra_path_length(self.graph, *key)
        return self.cache[key]

    def path(self, src: str, dst: str) -> List[str]:
        if src == dst:
            return [src]
        return nx.dijkstra_path(self.graph, src, dst)

    def __contains__(self, item):
        return item in self.graph


GRAPH = Graph()
