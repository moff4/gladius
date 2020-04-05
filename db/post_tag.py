from pony import orm
from datetime import datetime

from conf import conf

from .post import Post
from .tag import Tag


class PostTag(conf.sql.Entity):
    _table_ = ('hashtag', 'post_tag')

    post = orm.Required(Post, reverse='tags')
    tag = orm.Required(Tag, reverse='posts')
    created = orm.Optional(datetime)

    @staticmethod
    def rank_weights(tag):
        res = [
            float(i) if i is not None else 0.0
            for i in conf.sql.select(
                '''SELECT
                        count(p.post_id),
                        sum(p.views),
                        sum(p.likes),
                        sum(p.reposts)
                    FROM (
                        select * from hashtag.post_tag
                        where tag = $(tag)
                    ) pt left join hashtag.post p
                    on pt.post = p.post_id;
                '''
            )[0]
        ]
        return [
            (res[0] / res[1]) if res[1] else 0.0,
            (res[0] / res[2]) if res[2] else 0.0,
            (res[0] / res[3]) if res[3] else 0.0,
        ]
