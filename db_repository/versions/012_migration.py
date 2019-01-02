from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('p_id', INTEGER, primary_key=True, nullable=False),
    Column('p_board', INTEGER),
    Column('p_usrid', INTEGER),
    Column('p_title', VARCHAR(length=255)),
    Column('p_clickcnt', INTEGER),
    Column('p_replycnt', INTEGER),
    Column('p_content', TEXT),
)

board = Table('board', pre_meta,
    Column('b_id', INTEGER, primary_key=True, nullable=False),
    Column('b_name', VARCHAR(length=255), nullable=False),
    Column('b_postcnt', INTEGER),
)

user = Table('user', pre_meta,
    Column('usr_id', INTEGER, primary_key=True, nullable=False),
    Column('usr_password', VARCHAR(length=255)),
    Column('usr_name', VARCHAR(length=255)),
    Column('usr_birthday', VARCHAR(length=255)),
    Column('usr_gender', VARCHAR(length=255)),
    Column('usr_age', SMALLINT),
    Column('usr_email', VARCHAR(length=255)),
    Column('usr_level', INTEGER),
    Column('usr_role', SMALLINT),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['p_id'].drop()
    pre_meta.tables['board'].columns['b_id'].drop()
    pre_meta.tables['user'].columns['usr_age'].drop()
    pre_meta.tables['user'].columns['usr_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['p_id'].create()
    pre_meta.tables['board'].columns['b_id'].create()
    pre_meta.tables['user'].columns['usr_age'].create()
    pre_meta.tables['user'].columns['usr_id'].create()
