-------------------table (authors)--------------------

# the number of authors
1.1
select count(full_name)
from authors
# the result:
  -----> 845

1.2
# authors and documents
select full_name, title, count(title)
from authors a, documents b, documents_authors c
where a.id=c.authors_id and c.documents_id=b.id
group by full_name
order by count(title) desc


1.3
# authors and keywords
select full_name, keyword, count(keyword)
from authors a, documents b, documents_authors c, keywords k, documents_keywords kd
where a.id=c.authors_id and c.documents_id=b.id and k.id=kd.keyword_id and b.id = kd.keyword_id
group by full_name
order by count(keyword) desc


1.4
# institution and authors
select institution, full_name, count(full_name)
from authors
group by institution
order by count(full_name) desc

1.5
# institution and documents
select institution, title, count(title)
from authors a, documents b, documents_authors c
where a.id=c.authors_id and b.id=c.documents_id
group by institution
order by count(title) desc

1.6
# institution and keywords
select distinct institution, keyword, count(keyword)
from authors a, documents b, documents_authors c, keywords k, documents_keywords kd
where a.id=c.authors_id and c.documents_id=b.id and k.id=kd.keyword_id and b.id = kd.keyword_id
group by institution
order by count(keyword) desc


1.7
#the documents without institution records
select institution, full_name
from authors
where institution = ''



-----------------table  (documents) --------------------

# the number of documents
2.1
select count(title)
from documents
#  results----> 1305

#  however, there is a column named article_id, values vary from 1801 to 3291.
#  the difference is 1491. some article are missed. The reason is not found by now.


2.2
# the documents and their authors
select title, full_name, count(full_name)
from authors a, documents_authors b, documents c
where a.id=b.authors_id and c.id = b.documents_id
group by title
order by count(full_name) desc

2.3
# the documents from "author" ---"MIS//Qurterly"
select title 
from documents, documents_authors b, authors c
where documents.id=b.documents_id and c.id=b.authors_id and c.full_name= "MIS//Quarterly"




----------------table (journals)-----------------
3
select distinct volume, count(label)
from journals
group by volume
order by volume 


---------------table (keywords)------------------

#keywords and document (which keyword has max documents)
select keyword, title, article_id, count(title)
from documents doc, documents_keywords dk, keywords kw
where doc.id=dk.documents_id and  kw.id=dk.keyword_id
group by keyword
order by count(title) desc



------------------------------------------------
------------------------------------------------
------------#using the time line#---------------

select title, datepart('yyyy', pubilcation_date) as year
from documents


#   !!!!!!
#the datepart() function cannot be called in my mac somehow.
#this part should connect the elements with time line.


#and the year(), month() funcation cannot be called, either.


# the remainder should be connect keywords, institution and authors with time in year unit, decade unit.



