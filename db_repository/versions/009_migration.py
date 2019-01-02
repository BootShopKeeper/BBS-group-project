from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
migration_tmp = Table('migration_tmp', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('timestamp', DATETIME),
    Column('user_id', INTEGER),
)

post = Table('post', post_meta,
    Column('p_id', Integer, primary_key=True, nullable=False),
    Column('p_board', Integer),
    Column('p_usrid', Integer),
    Column('p_title', String(length=255)),
    Column('p_clickcnt', Integer, default=ColumnDefault(0)),
    Column('p_replycnt', Integer, default=ColumnDefault(0)),
    Column('p_content', Text),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=60)),
    Column('email', VARCHAR(length=120)),
    Column('role', SMALLINT),
    Column('password', INTEGER),
)

user = Table('user', post_meta,
    Column('usr_id', Integer, primary_key=True, nullable=False),
    Column('usr_password', String(length=255)),
    Column('usr_name', String(length=255)),
    Column('usr_birthday', String(length=255)),
    Column('usr_gender', String(length=255)),
    Column('usr_age', SmallInteger),
    Column('usr_email', String(length=255)),
    Column('usr_level', Integer),
    Column('usr_role', SmallInteger, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].drop()
    post_meta.tables['post'].create()
    pre_meta.tables['user'].columns['email'].drop()
    pre_meta.tables['user'].columns['id'].drop()
    pre_meta.tables['user'].columns['nickname'].drop()
    pre_meta.tables['user'].columns['password'].drop()
    pre_meta.tables['user'].columns['role'].drop()
    post_meta.tables['user'].columns['usr_age'].create()
    post_meta.tables['user'].columns['usr_birthday'].create()
    post_meta.tables['user'].columns['usr_email'].create()
    post_meta.tables['user'].columns['usr_gender'].create()
    post_meta.tables['user'].columns['usr_id'].create()
    post_meta.tables['user'].columns['usr_level'].create()
    post_meta.tables['user'].columns['usr_name'].create()
    post_meta.tables['user'].columns['usr_password'].create()
    post_meta.tables['user'].columns['usr_role'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].create()
    post_meta.tables['post'].drop()
    pre_meta.tables['user'].columns['email'].create()
    pre_meta.tables['user'].columns['id'].create()
    pre_meta.tables['user'].columns['nickname'].create()
    pre_meta.tables['user'].columns['password'].create()
    pre_meta.tables['user'].columns['role'].create()
    post_meta.tables['user'].columns['usr_age'].drop()
    post_meta.tables['user'].columns['usr_birthday'].drop()
    post_meta.tables['user'].columns['usr_email'].drop()
    post_meta.tables['user'].columns['usr_gender'].drop()
    post_meta.tables['user'].columns['usr_id'].drop()
    post_meta.tables['user'].columns['usr_level'].drop()
    post_meta.tables['user'].columns['usr_name'].drop()
    post_meta.tables['user'].columns['usr_password'].drop()
    post_meta.tables['user'].columns['usr_role'].drop()
