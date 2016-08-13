
from models import Document, Author, Keyword, Field, Journal
from parse import parseXML2dict as par

# take absolute path and session as input
# return nothing
# but add all the entries to the database session

def pipeline(abspath,session):
    
    #par() is parseXML_diclist() import from parse.py
    d=par(abspath)
    
    # d["Document"] is a list of dictionary
    # as there is only one dict in this list.
    # so by d['Document'][0]
    # we directly get a document_dictionary: doc. 
    
    doc=d["Document"][0]
    
    # the argument **doc is keyword argument.
    # we initialize Document with dictionary: doc
    # then we get a model object doc_t
    doc_t=Document(**doc)

    # this object should be add to session, otherwise you cannot find it in session.
    session.add(doc_t)
    
    # jour is the same pattern.
    jour=d['Journal'][0]
    jour_t=Journal(**jour)
    
    # here, for the documents column, we add doc_t to it.
    jour_t.documents.append(doc_t)
    
    session.add(jour_t)

    
    # we use loop here, because len(d['Author']) != 1
    for auth in d["Author"]:
        # we first check whether there is the same author in this session
        auth_t = session.query(Author).filter_by(full_name=auth["full_name"]).first()
        if auth_t == None:
            auth_t = Author(**auth)
        
        # if there exits this author, update his or her information
        else:
            for k, v in auth.items():
                auth_t.__setattr__(k,v)
                
        # append doc_t
        auth_t.documents.append(doc_t)
        session.add(auth_t)
    
    
    for key in d["Keyword"]:
        # some documents may not have keywords
        # if we omit this line, an Error will be raised.
        if len(key) != 0:
            
            key_t=session.query(Keyword).filter_by(keyword=key["keyword"]).first()
            if key_t == None:
                key_t = Keyword(**key)
            else:
                for k,v in key.items():
                    key_t.__setattr__(k,v)
            key_t.documents.append(doc_t)
            session.add(key_t)
    
    
    for fld in d["Field"]:
        fld_t=session.query(Field).filter_by(name=fld["name"],value=fld["value"],type=fld["type"]).first()
        if fld_t == None:
            fld_t = Field(**fld)
        else:
            for k,v in fld.items():
                fld_t.__setattr__(k,v)
        fld_t.documents.append(doc_t)
        session.add(fld_t)



