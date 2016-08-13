from lxml import etree

# first is get five table-blocks from ElementTree

xpv_blocks = [".//document", 
              ".//author",
              ".//keyword",
              ".//field",
              ".//submission-path"]


# we need five list of xpath, because we need five tables.
# the elements in each list are the column value for each table

xpv_document = ["title/text()", 
                "abstract/text()", 
                "publication-title/text()", 
                "publication-date/text()",
                "submission-date/text()", 
                "coverpage-url/text()", 
                "fulltext-url/text()", 
                "fpage/text()", 
                "lpage/text()",
                "document-type/text()", 
                "type/text()", 
                "articleid/text()",
                "context-key/text()",
                "submission-path/text()",
                "label/text()"]

xpv_author = ["fname/text()", 
              "mname/text()",
              "lname/text()",
              "email/text()", 
              "institution/text()"]
             
xpv_keyword = ["text()"]

xpv_field = ["@name", 
             "@type", 
             "value/text()"]

# here is a special table: journal table
# because we cannot get dbv_journal from xpv_journal by the function I will introduce soon.
xpv_journal = ["text()"]

dbv_journal = ["domain", 
               "vol", 
               "iss", 
               "label"]



def xpv2dbv(xpv):
    dbv = list(xpv)
    # must add list() before xpv.
    # because xpv is a list, which is mutable
    # without list(), xpv will be changed, which means the same as dbv
    
    
    for i in range(len(dbv)):
    # every element in the input list, must be modified
        if "text()" in dbv[i]:
            dbv[i]=dbv[i].replace("text()", '')
        if "@" in dbv[i]:
            dbv[i]=dbv[i].replace("@",'')
        if "-" in dbv[i]:
            dbv[i]=dbv[i].replace('-','_')
        if"." in dbv[i]:
            dbv[i]=dbv[i].replace(".",'')
        if"/" in dbv[i]:
            dbv[i]=dbv[i].replace('/','')
    return dbv




# for this function, we input a list of element
# then each element is transformed to a dictionary.
# and finially, a list of dictionaries are returned.


# blocksdict is a dictionary following the pattern from file to blocks.
# keys are keys of blocksdict as well as table labels.
# xpv is a list of xpath.
# dbv = None, which can be indicated, otherwise.


def ele2dictlist(blocksdict, key, xpv, dbv=None):
    dictlist = []
    if dbv == None:
        dbv = xpv2dbv(xpv)
        
        
    # this 'if' block is used to handle the special case, which will be explained soon.
    if key == "submission_path":
        
        # ele is the first element in the list
        ele = blocksdict[key][0]
        # xpv is a list
        raw = ele.xpath(xpv[0]) 
        elelist = raw[0].split('/')
        dictlist.append(dict((zip(dbv, elelist))))
        return dictlist
    
    for ele in blocksdict[key]:
        elelist = list(map(ele.xpath, xpv))
        for i in range(len(elelist)):
            tem = elelist[i]
            try:
                elelist[i] = tem[0]
            except:
                elelist[i] = ''
        eledict = dict(zip(dbv, elelist))
        
        dictlist.append(eledict)

    return dictlist
    



# integrate all together

# input: abspath of XML file is the only argument.
# output: a dictionary where values are lists of element-dictionaries.

def parseXML2dict(abspath):
    
    # get blocksdict from file
    tree = etree.parse(abspath)
    
    blockslist = list(map(tree.xpath, xpv_blocks)) # xpv_blocks from setting.
    dbv_blocks = xpv2dbv(xpv_blocks)               # xpv2dbv() from setting
    blocksdict = dict(zip(dbv_blocks, blockslist))
    #generate the diclist

    # document_dictlist
    doc_dict = ele2dictlist(blocksdict,"document",xpv_document) # function ele2dictlist() from setting.
    for i in doc_dict:
        try:
            i["pages"]=str(int(i["lpage"])-int(i["fpage"])+1)
        except:
            i["pages"]=''

    # author_dictlist
    auth_dict = ele2dictlist(blocksdict,"author",xpv_author)
    for i in auth_dict:
        i["full_name"]=i['fname']+'/'+i["mname"]+'/'+i['lname']

    # field_dictlist
    fid_dict = ele2dictlist(blocksdict,"field",xpv_field)

    # key_dictlist
    key_dict = ele2dictlist(blocksdict,"keyword",xpv_keyword)
    for i in key_dict:
        for j in i.keys():
            if j=='':
                i["keyword"]=i[j]
                i.pop(j)           

    # journal_dictlist
    jour_dict = ele2dictlist(blocksdict,"submission_path",xpv_journal,dbv=dbv_journal)

    return dict(zip(["Document","Author","Journal","Field","Keyword"],[doc_dict, auth_dict, jour_dict, fid_dict, key_dict]))



    