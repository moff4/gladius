
from collections import defaultdict

from conf import conf


SQL_LOAD_NEAREST = '''
SELECT distinct pt1.tag, pt2.tag
FROM (
    select *
    from hashtag.post_tag
    where tag in (%s)
) pt1 inner join hashtag.post_tag pt2 on pt1.post = pt2.post
and pt1.tag != pt2.tag
'''

LOAD_LIMIT = 50


class Clustering:
    def __init__(self):
        # tag -> set of neighboors
        self.__near = defaultdict(set)
        self._loaded = set()
        self._queue = set()

    def nears(self, tag: str) -> set:
        if tag in self._loaded:
            return self.__near[tag]
        tags = [tag]
        for i, t in enumerate(self._queue - self._loaded):
            tags.append(t)
            if i > LOAD_LIMIT:
                break

        conn = conf.sql.get_connection()
        cur = conn.cursor()
        cur.execute(SQL_LOAD_NEAREST % ','.join(['%s'] * len(tags)), tags)
        row = cur.fetchone()
        while row is not None:
            self.__near[(t := row[0])].add(row[1])
            if t in self._queue:
                self._queue.remove(row[0])
            row = cur.fetchone()
        self._loaded.update(tags)
        return self.__near[tag]

    def clustering_coeff(self, tag: str) -> float:
        near = self.nears(tag)
        self._queue.update(near)
        k = len(near)
        if k <= 1:
            c = 1.0
        else:
            fr_eges = {
                '@'.join([i, j] if i > j else [j, i])
                for i in near
                for j in (near & self.nears(i))
            }
            c = 2 * len(fr_eges) / (k * (k - 1))
        return c
