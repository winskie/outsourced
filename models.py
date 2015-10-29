#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Text
from database import Base

class LikedPhoto(Base):
	__tablename__ = 'liked_photos'
	id = Column(Integer, primary_key = True)
	title = Column(String(255))
	author = Column(String(255))
	photo_url = Column(String(255))
	link = Column(String(255))
	tags = Column(Text)
	user_id = Column(String(20))
	
	def __init__(self, id=None, title=None, author=None, photo_url=None,
	             link=None, tags=None, user_id=None):
		self.id = id
		self.title = title
		self.author = author
		self.photo_url = photo_url
		self.link = link
		self.tags = tags
		self.user_id = user_id
		
	def __repr__(self):
		return "<Photo %r>" % (self.title)