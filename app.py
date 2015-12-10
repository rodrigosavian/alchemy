from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logging.basicConfig()
logger = logging.getLogger("myapp.sqltime")
logger.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s", statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f", total)

class A(Base):
    __tablename__ = 'A'

    id = Column('id', Integer, primary_key=True)

class B(Base):
    __tablename__ = 'B'

    id = Column('id', Integer, primary_key=True)
    a_id = Column('a_id', ForeignKey(A.id))
    a = relationship(A, lazy='joined')

class C(Base):
    __tablename__ = 'C'

    id = Column('id', Integer, primary_key=True)
    b_id = Column('b_id', ForeignKey(B.id))
    b = relationship(B)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('mysql+mysqldb://root:@localhost/sqlalchemy')
Session = sessionmaker(bind=engine)
session = Session()

# q = session.query(A).join(B).join(C).filter(B.id==2)
# print([x.id for x in q.all()])
# 
# 
# print('ok')
from sqlalchemy.orm import joinedload
q1 = session.query(C).join(B).join(A).options(joinedload(C.b)).filter(B.id==1)
print([(x.id, x.b.id, x.b.a.id) for x in q1.all()])
