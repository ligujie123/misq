from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os


Base= declarative_base()



def db_connect(basedir):
	return create_engine('sqlite:///'+os.path.join(basedir, 'data.sqlite'))

def create_table(engine):
	Base.metadata.create_all(engine)

documents_authors = Table('documents_authors', Base.metadata,
		Column('documents_id', ForeignKey("documents.id"), primary_key=True),
		Column('authors_id', ForeignKey("authors.id"), primary_key=True))

documents_keywords=Table("documents_keywords",Base.metadata,
		Column("documents_id", ForeignKey("documents.id"),primary_key=True),
		Column("keyword_id", ForeignKey('keywords.id'), primary_key=True))

documents_fields=Table('documents_fields', Base.metadata,
		Column('documents_id',ForeignKey('documents.id'),primary_key=True),
		Column('fields_id',ForeignKey('fields.id'), primary_key=True))


class Document(Base):
	__tablename__='documents'

	id = Column(Integer, primary_key=True)

	title=Column('title', String)

	abstract=Column('abstract', String)

	publication_date=Column("publication_date", String)
	#the tag is "publication-date"

	submission_date=Column("submission_date", String)
	#the tag is "submission-date"

	coverpage_url=Column("cover_url", String)
	fulltext_url=Column("full_url", String)

	fpage=Column("first_page", String)
	lpage=Column("last_page", String)
	pages=Column("pages", String)

	document_type=Column("document_type", String)
	#the tag is document-type

	type=Column("type", String)
	articleid=Column("article_id",String)

	context_key=Column("context_key", String)
	#the tag is context-key

	label=Column("label", String)

	publication_title=Column(String)


	submission_path=Column("submission_path", String) 
	#the tag is submission-path
	#need to be specified here as well as expanded.

	keywords=relationship("Keyword",
						secondary=documents_keywords,
						back_populates="documents")	
											#another table
	fields=relationship('Field',
						secondary=documents_fields,
						back_populates="documents")
													#another table
	authors=relationship("Author", 
						secondary=documents_authors,
						back_populates="documents")

							#another table
	journal_id=Column(Integer, ForeignKey('journals.id'))

	journal=relationship("Journal", back_populates="documents")
							#many to one type here. need to be combined with the first denoted one

	def __repr__(self):
		return "<Document(title=%r)>" %self.title



'''
class Co_Author(Base):
	__tablename__="co_authors"

	his_senior_collegue_id=Column(Integer, 
						ForeignKey=('authors.id'),
						primary_key=True)

	his_junior_collegue_id=Column(Integer,
						ForeignKey=('authors.id'),
						primary_key=True)

	his_peer_collegue_id=Column(Integer,
						ForeignKey=("authors.id"),
						primary_key=True)
'''

class Author(Base):
	__tablename__='authors'

	id= Column(Integer,primary_key=True)

	email=Column("email", String)
	institution=Column("institution", String)

	lname=Column("last_name", String)
	fname=Column("first_name", String)
	mname=Column("middle_name", String)

	full_name=Column("full_name", String, nullable=True)

	documents=relationship('Document', 
						secondary=documents_authors,
						back_populates="authors")

							#m:m
	'''

	his_senior_collegues=relationship("Co_Author",
						foreign_keys=[Co_Author.his_senior_collegue_id],
						back_populates=)					#m:m

															#this part needs some more considerations
	his_peer_collegues=relationship()

	his_junior_collegues=relationship()

	'''

	def __repr__(self):
		return "<Author(full_name=%r)>" %self.full_name






class Keyword(Base):
	__tablename__="keywords"

	id=Column(Integer, primary_key=True)

	keyword=Column(String)

	documents=relationship("Document",
						secondary=documents_keywords,
						back_populates="keywords")
											#m:m

	def __repr__(self):
		return "<Keyword(keyword=%r)>" %self.keyword
		#the methods may be wrong!



class Field(Base):
	__tablename__='fields'
	id=Column(Integer, primary_key=True)

	name=Column('name',String)
	type=Column('type',String)
	value=Column('value',String)
	documents=relationship('Document',
						secondary=documents_fields,
						back_populates="fields")
	def __repr__(self):
		return "<Field(name=%r, type=%r, value=%r)>" %(self.name, self.type, self.value)
	#m:m

	#def __repr__(self):
	#	return "<Field(name='%r', type='%r', value='%r', frequency='%d')>"(self.name, self.type, self.value, self.documents.counts())


class Journal(Base):
	__tablename__='journals'
	id=Column(Integer, primary_key=True)
	domain=Column("domain",String)
	vol=Column("volume", String)
	iss=Column('issue', String)
	label=Column('label', String)

	documents=relationship("Document", back_populates="journal")						#1:m

	def __repr__(self):
		return "<Journal(vol %r, iss %r)>" %(self.vol, self.iss)
