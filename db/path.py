from pony import orm

from conf import conf

from .tag import Tag


class Path(conf.sql.Entity):
    _table_ = ('hashtag', 'path')

    src = orm.Required(Tag, reverse='path_src')
    dst = orm.Required(Tag, reverse='path_dst')
    tag = orm.Required(Tag, reverse='path_in')
    pos = orm.Required(int)  # 0 - src, max - dst
    orm.PrimaryKey(src, dst, tag)
