
from pony import orm

from conf import conf


class Post(conf.sql.Entity):
    _table_ = ('hashtag', 'post')

    post_id = orm.PrimaryKey(str)
    post_date = orm.Required(int)
    views = orm.Required(int)
    likes = orm.Required(int)
    reposts = orm.Required(int)
    timestamp = orm.Required(int)
    from_group = orm.Required(bool, nullable=True)
    tags = orm.Set('PostTag')
