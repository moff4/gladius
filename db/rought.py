
from pony import orm

from conf import conf


class Rought(conf.sql.Entity):
    _table_ = ('hashtag', 'rought')

    tag1 = orm.Required(str)
    tag2 = orm.Required(str)
    weight = orm.Required(float)
    orm.PrimaryKey(tag1, tag2)

    @staticmethod
    def create_multi(roughts):
        if roughts:
            sql = '''
                INSERT INTO `rought` (`tag1`, `tag2`, `weight`) values %s
                ON DUPLICATE KEY UPDATE
                `tag1` = values(`tag1`),
                `tag2` = values(`tag2`),
                `weight` = values(`weight`)
            ''' % (
                ','.join(['(%s)' % ','.join(['%s'] * len(row)) for row in roughts])
            )
            con = conf.sql.get_connection()
            cur = con.cursor()
            cur.execute(sql, [arg for row in roughts for arg in row])
            cur.close()
            con.commit()
