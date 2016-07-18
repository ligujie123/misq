from models import Document, Author, Keyword, Field, Journal
from parse import parseXML_diclist as par

def pipeline(abspath,session):
    d=par(abspath)#par() is parseXML_diclist() import from parse.py
    doc=d["Document"][0]
    doc_t=Document(**doc)
    session.add(doc_t)
    
    jour=d['Journal'][0]
    jour_t=Journal(**jour)
    jour_t.documents.append(doc_t)
    session.add(jour_t)

    
    for auth in d["Author"]:
        auth_t=session.query(Author).filter_by(full_name=auth["full_name"]).first()
    if auth_t==None:
        auth_t=Author(**auth)
    else:
        for k, v in auth.items():
            auth_t.__setattr__(k,v)
    auth_t.documents.append(doc_t)
    session.add(auth_t)
    
    
    for key in d["Keyword"]:
        key_t=session.query(Keyword).filter_by(keyword=key["keyword"]).first()
    if key_t== None:
        key_t = Keyword(**key)
    else:
        for k,v in key.items():
            key_t.__setattr__(k,v)
    key_t.documents.append(doc_t)
    session.add(key_t)
    
    
    for fld in d["Field"]:
        fld_t=session.query(Field).filter_by(name=fld["name"],value=fld["value"],type=fld["type"]).first()
    if fld_t== None:
        fld_t = Field(**fld)
    else:
        for k,v in fld.items():
            fld_t.__setattr__(k,v)
    fld_t.documents.append(doc_t)
    session.add(fld_t)
    
	






