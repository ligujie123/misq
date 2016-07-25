#-----------table (authors)-------

# authors and documents
select full_name, title, count(title)
from authors a, documents b, documents_authors c
where a.id=c.authors_id and c.documents_id=b.id
group by full_name
order by count(title) desc



# authors and keywords
select full_name, keyword, count(keyword)
from authors a, documents b, documents_authors c, keywords k, documents_keywords kd
where a.id=c.authors_id and c.documents_id=b.id and k.id=kd.keyword_id and b.id = kd.keyword_id
group by full_name
order by count(keyword) desc



# institution and authors
select institution, full_name, count(full_name)
from authors
group by institution
order by count(full_name) desc


# institution and documents
select institution, title, count(title)
from authors a, documents b, documents_authors c
where a.id=c.authors_id and b.id=c.documents_id
group by institution
order by count(title) desc


# institution and keywords
select distinct institution, keyword, count(keyword)
from authors a, documents b, documents_authors c, keywords k, documents_keywords kd
where a.id=c.authors_id and c.documents_id=b.id and k.id=kd.keyword_id and b.id = kd.keyword_id
group by institution
order by count(keyword) desc

#the documents without institution records
select institution, full_name
from authors
where institution = ''


#＊＊＊＊＊＊table ----documents
# the documents and their authors
select title, full_name, count(full_name)
from authors a, documents_authors b, documents c
where a.id=b.authors_id and c.id = b.documents_id
group by title
order by count(full_name) desc


# the documents from "author" ---"MIS//Qurterly"
select title 
from documents, documents_authors b, authors c
where documents.id=b.documents_id and c.id=b.authors_id and c.full_name= "MIS//Quarterly"





#****  ---table journals
select distinct volume, count(label)
from journals
group by volume
order by volume 


#**** ---table keywords

#keywords and document (which keyword has max documents)
select keyword, title, article_id, count(title)
from documents doc, documents_keywords dk, keywords kw
where doc.id=dk.documents_id and  kw.id=dk.keyword_id
group by keyword
order by count(title) desc





#using the time line#

select title, datepart('yyyy', pubilcation_date) as year
from documents

#the datepart() function cannot be called in my mac somehow.
#this part should connect the elements with time line.

