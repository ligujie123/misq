# to get the database's absolute path.
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# for building the basic mapping table classes.
from sqlalchemy import Column, String, Integer, Table

# for building relationships among tables.
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



# create_engine need database URI as the augument.
# sqlite3's URI form (for Mac) is such: 'sqlite:////absolute/path/to/database'

def db_connect(basedir, name = 'data'):
    return create_engine('sqlite:///'+os.path.join(basedir, name + '.sqlite'))


# we get Base from the initializaiton of class declarative_base
# Base will be the basic table which will be extended to other tables
# then we connect this basic table to the engine.

Base= declarative_base()

def create_table(engine):
    Base.metadata.create_all(engine)
    
    

# construct register table
documents_authors = Table('documents_authors', Base.metadata,
                          Column('documents_id', ForeignKey("documents.id"), primary_key=True),
                          Column('authors_id', ForeignKey("authors.id"), primary_key=True))

documents_keywords = Table("documents_keywords",Base.metadata,
                           Column("documents_id", ForeignKey("documents.id"),primary_key=True),
                           Column("keyword_id", ForeignKey('keywords.id'), primary_key=True))

documents_fields = Table('documents_fields', Base.metadata,
                         Column('documents_id',ForeignKey('documents.id'),primary_key=True),
                         Column('fields_id',ForeignKey('fields.id'), primary_key=True))




# documents table
class Document(Base):
    #### This part is not change, is the same as above ####
    __tablename__='documents'

    # every column is an object of class Column
    # Integer, String: datatype
    # 'title', 'abstract': column label. optional
    id = Column(Integer, primary_key=True)

    title=Column('title', String)

    abstract=Column('abstract', String)

    publication_date=Column("publication_date", String)

    submission_date=Column("submission_date", String)

    coverpage_url=Column("cover_url", String)
    fulltext_url=Column("full_url", String)

    fpage=Column("first_page", String)
    lpage=Column("last_page", String)
    pages=Column("pages", String)

    document_type=Column("document_type", String)

    type=Column("type", String)
    articleid=Column("article_id",String)

    context_key=Column("context_key", String)

    label=Column("label", String)

    publication_title=Column(String)

    submission_path=Column("submission_path", String) 
    ##### So you can skip this part ####
    
    
    # this is corresponding to the register table above.
    # here we use the relationship() method
    
    authors=relationship("Author", 
                         secondary=documents_authors,
                         back_populates="documents")
    
    keywords=relationship("Keyword",
                          secondary=documents_keywords,
                          back_populates="documents")
    
    fields=relationship('Field',
                        secondary=documents_fields,
                        back_populates="documents")
    
    journal_id=Column(Integer, ForeignKey('journals.id'))
    journal=relationship("Journal", back_populates="documents")
    
    def __repr__(self):
        return "<Document(title=%r)>" %self.title

# authors table
class Author(Base):
    __tablename__='authors'
    #### this part is in the same pattern of document table ####
    id= Column(Integer,primary_key=True)
    
    email=Column("email", String)
    institution=Column("institution", String)
    
    lname=Column("last_name", String)
    fname=Column("first_name", String)
    mname=Column("middle_name", String)
    full_name=Column("full_name", String, nullable=True)
    ### these are mapping columns, the column labels are from the list: dbv_author. ###
    
    
    
    documents=relationship('Document', 
                           secondary=documents_authors,
                           back_populates="authors")
    
    def __repr__(self):
        return "<Author(full_name=%r)>" %self.full_name
    
    
    
# keywords table      
class Keyword(Base):
    __tablename__="keywords"
    id=Column(Integer, primary_key=True)
    
    keyword=Column(String)
    
    documents=relationship("Document",
                           secondary=documents_keywords,
                           back_populates="keywords")
    
    def __repr__(self):
        return "<Keyword(keyword=%r)>" %self.keyword

    
    
    
# fields table
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

    
    
class Journal(Base):
    __tablename__='journals'
    id=Column(Integer, primary_key=True)
    
    domain=Column("domain",String)
    vol=Column("volume", String)
    iss=Column('issue', String)
    label=Column('label', String)
    
    documents=relationship("Document", back_populates="journal")
    
    def __repr__(self):
        return "<Journal(vol %r, iss %r)>" %(self.vol, self.iss)
    
    