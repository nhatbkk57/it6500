import logging
import sys
import json

# External Imports
from sqlalchemy import Column
from sqlalchemy.types import String, Integer, Float, BigInteger, Text,DateTime, JSON
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.dialects.postgresql import JSON

engine = create_engine('postgres://koflhifh:9M-7ZYR0oGcJ-NN7q52oyDsSU9Bd0GiB@horton.elephantsql.com:5432/koflhifh')
Session = scoped_session(sessionmaker(engine))
DeclarativeBase = declarative_base(engine)
# Add query functionality to base model
DeclarativeBase.query = Session.query_property()

class User(DeclarativeBase):
	__tablename__ = "user"
	user_id = Column(BigInteger, autoincrement=True, primary_key=True)
	user_name = Column(String)


class ImageStorage(DeclarativeBase):
	__tablename__ = 'image_storage'
	photo_id = Column(String,primary_key=True)
	photo_link = Column(Text)
	created_at = Column(DateTime)
	user_id = Column(Integer)
	meta_labels = Column(JSON)
	width = Column(Integer)
	height = Column(Integer)
	

class ImageLabel(DeclarativeBase):

	__tablename__ = 'image'
	id = Column(BigInteger, autoincrement=True, primary_key=True)
	photo_id = Column(String)
	label_id = Column(Integer)
	# lower_case standard
	label_text = Column(String)
	bound_bnx = Column(JSON)
	confidence = Column(Float)


def syncdb():
    logging.info('Initialising the database.')
 
    DeclarativeBase.metadata.create_all(engine)

def save(list_objects):
	try:	
		for item in list_objects:
			Session.add(item)
		Session.commit()
	except Exception as e:
		print(e)
    # Query
    # Session.execute('select * from events')
    # engine.execute(vipul.insert(), id=1, name='ddd', fullname='swee')

if __name__ == "__main__":
    syncdb()







