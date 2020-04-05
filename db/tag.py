from datetime import datetime
from pony import orm

from conf import conf


class Tag(conf.sql.Entity):
    _table_ = ('hashtag', 'tag')

    tag = orm.PrimaryKey(str)
    created = orm.Optional(datetime)
    checked = orm.Optional(int)
    rank_pop = orm.Optional(float, nullable=True)
    rank_qual = orm.Optional(float, nullable=True)
    clustering = orm.Optional(float, nullable=True)
    frequency = orm.Optional(float, nullable=True)

    posts = orm.Set('PostTag')
    nears = orm.Set('TagTagMap')
    nears_ = orm.Set('TagTagMap')
    path_src = orm.Set('Path')
    path_dst = orm.Set('Path')
    path_in = orm.Set('Path')
