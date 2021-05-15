from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import sys
import MySQLdb

DATABASE = 'mysql://root:@localhost/parm_reading'

# setup sqlalchemy
engine = create_engine(DATABASE, encoding='utf-8', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# テーブルクラス


class ParmInfo(Base):
    __tablename__ = 'parm_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column('userid', String(100))
    has_parm_image = Column('has_parm_image', Boolean, default=False)
    is_data_available = Column('is_data_available', Boolean, default=False)
    answer1 = Column('answer1', Integer)
    answer2 = Column('answer2', Integer)
    answer3 = Column('answer3', Integer)
    answer4 = Column('answer4', Integer)
    answer5 = Column('answer5', Integer)
    answer6 = Column('answer6', Integer)
    answer7 = Column('answer7', Integer)
    answer8 = Column('answer8', Integer)
    answer9 = Column('answer9', Integer)
    answer10 = Column('answer10', Integer)

    def __init__(self, userid, has_parm_image, is_data_available, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10):
        self.userid = userid
        self.has_parm_image = has_parm_image
        self.is_data_available = is_data_available
        self.answer1 = answer1
        self.answer2 = answer2
        self.answer3 = answer3
        self.answer4 = answer4
        self.answer5 = answer5
        self.answer6 = answer6
        self.answer7 = answer7
        self.answer8 = answer8
        self.answer9 = answer9
        self.answer10 = answer10

    def __repr__(self):
        return "<Parminfo('%s','%s','%s', '%s','%s', '%s', '%s')>" % (self.userid, self.has_parm_image, self.is_data_available, self.answer1, self.answer2, self.answer3, self.answer4)


def insert_info(userid):
    if db_session.query(ParmInfo).filter_by(userid=userid).scalar() is None:
        add_user = ParmInfo(userid, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        db_session.add(add_user)
        db_session.commit()


def update_info(userid, update_column, update_content):
    if db_session.query(ParmInfo).filter_by(userid=userid).scalar() is None:
        insert_info(userid)
    update_user = db_session.query(ParmInfo).filter(
        ParmInfo.userid == userid).first()
    setattr(update_user, update_column, update_content)
    db_session.commit()


def delete_info(userid):
    db_session.query(ParmInfo).filter_by(userid=userid).delete()
    db_session.commit()


def is_has_image(userid):
    user = db_session.query(ParmInfo).filter(userid == userid).first()
    return user.has_parm_image


def is_complete_answer(userid):
    user = db_session.query(ParmInfo).filter(userid == userid).first()
    answer_list = [user.answer1, user.answer2, user.answer3, user.answer4]
    return False if 0 in answer_list else True


def get_db_id(userid):
    user = db_session.query(ParmInfo).filter(userid == userid).first()
    return user.id
