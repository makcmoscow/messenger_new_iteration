import enum
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData,UniqueConstraint, Enum
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.exc import IntegrityError as NotUniq
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///test2_db.sqlite', echo=False)
Session = sessionmaker(bind=engine)



class User(Base):
    __tablename__ = 'users_table'
    id = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False, unique=True)
    # login_name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)


    def __repr__(self):
        return "USER({}, {})".format(self.nickname, self.password)

    def create_database(self):
        Base.metadata.create_all(engine)

    def add_user(self):
        session = Session()
        session.add(self)
        try:
            session.commit()
        except NotUniq:
            print('this user already in database')
        finally:
            session.close()


    def get_user(self, nickname = None):
        session = Session()
        x = session.query(User).filter(User.nickname == nickname).first()
        session.close()
        return x

    def del_user(self, nickname = None):
        session = Session()
        x = session.query(User).filter(User.nickname == nickname).first()
        session.delete(x)
        session.commit()
        session.close()

if __name__ == '__main__':
    engine = create_engine('sqlite:///test2_db.sqlite', echo=False)
    Session = sessionmaker(bind=engine)
    user = User(nickname='123', password='789')
    user.create_database()
    user.add_user()


































# engine = create_engine('sqlite:///test_db.sqlite', echo = True)
# Session = sessionmaker(bind=engine)
#
# class Base:
#     def __init__(self):
#         pass
#
#
#     def get_users_table(self): # We about to create users table. If table already exist it wouldn't be rewritten
#         metadata = MetaData()
#         self.users_table = Table('users', metadata,
#                             Column('id', Integer, primary_key=True),
#                             Column('nickname', String),
#                             Column('login_name', String),
#                             Column('password', String),
#                             UniqueConstraint('nickname'))
#         metadata.create_all(engine)
#         return self.users_table
#
#     def add_user(self, user):
#         session = Session()
#         session.add(user)
#         try:
#             session.commit()
#         except NotUniq:
#             print('this user already in database')
#         finally:
#             session.close()
#
#     def get_user(self, nickname):
#         session = Session()
#         x = session.query(User).filter(User.nickname == nickname).first()
#         session.close()
#         return x
#
#     def del_user(self, nickname):
#         session = Session()
#         x = session.query(User).filter(User.nickname == nickname).first()
#         session.delete(x)
#         session.commit()
#         session.close()
# #
#
#
#
#
#
# class User:
#     def __init__(self, nickname, login_name, password):
#         self.nickname = nickname
#         self.login_name = login_name
#         self.password = password
#
#     def __repr__(self):
#         return "USER({}, {}, {})".format(self.nickname, self.login_name, self.password)

# users_table = Base().users_table

# base = Base()
# users_table_m = mapper(User, base.get_users_table())
# user = User('Leonardo', 'LeoPoldo', '321')
# base.add_user(user)
# x = base.get_user('Leo')
# print(x)
# base.del_user(x.nickname)
# base.get_user(user)


