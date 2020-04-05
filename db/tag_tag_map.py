from pony import orm

from conf import conf

from .tag import Tag


class TagTagMap(conf.sql.Entity):
    _table_ = ('hashtag', 'tag_tag_map')

    tag1 = orm.Required(Tag, reverse='nears')
    tag2 = orm.Required(Tag, reverse='nears_')
    posts_num = orm.Required(float)
    orm.PrimaryKey(tag1, tag2)
