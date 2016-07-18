from lxml import etree

#make xpath for every table
xp_document=["title/text()", "abstract/text()", "publication-title/text()", "publication-date/text()",\
             "submission-date/text()", "coverpage-url/text()", "fulltext-url/text()", "fpage/text()", \
              "lpage/text()","document-type/text()", "type/text()", "articleid/text()","context-key/text()",\
              "submission-path/text()","label/text()"]
#this is special
db_journal=["domain", "vol", "iss", "label"]
xp_journal=["text()"]

xp_author=("fname/text()", "mname/text()","lname/text()","email/text()", "institution/text()")
xp_keyword=["text()"]

xp_field=("@name", "@type", "value/text()")


def mod_xpath_var(l1):
    l2=list(l1)
    for i in range(len(l2)):
        if "text()" in l2[i]:
            l2[i]=l2[i].replace("text()", '')
        if "@" in l2[i]:
            l2[i]=l2[i].replace("@",'')
        if "-" in l2[i]:
            l2[i]=l2[i].replace('-','_')
        if"." in l2[i]:
            l2[i]=l2[i].replace(".",'')
        if"/" in l2[i]:
            l2[i]=l2[i].replace('/','')
    return l2



#this function is not fully capsulated, for we still need eledict from outside.
def get_list_of_dict(eledict,table,xpv,dbv=None):
    list_of_dict=[]
    if dbv==None:
        dbv=mod_xpath_var(xpv)
    if table=="submission_path":
        i=eledict[table][0]   #list
        rawvalue=i.xpath(xpv[0]) #list
        values=rawvalue[0].split('/')
        list_of_dict.append(dict((zip(db_journal,values))))
        return list_of_dict
    
    for ele in eledict[table]:
        values=[]
        for i in xpv:
            value=''
            tem=ele.xpath(i) 
            try:
                value=tem[0]
            except:
                pass

            values.append(value)
            dict_of_values=dict(zip(dbv,values))
        list_of_dict.append(dict_of_values)
    return list_of_dict
    
    


def parseXML_diclist(absolutepath):
	'''parse a file, generate a dict contains five lists which contain info for five tables'''
	tree = etree.parse(absolutepath)

	tables_xpath=[".//document", ".//author",".//keyword",".//field",".//submission-path"]
	table_vars=mod_xpath_var(tables_xpath)
	retn_list=list(map(tree.xpath, tables_xpath))
	eledict=dict(zip(table_vars, retn_list))




	#generate the diclist
	doc_dict=get_list_of_dict(eledict,"document",xp_document)
	for i in doc_dict:
		try:
			i["pages"]=str(int(i["lpage"])-int(i["fpage"])+1)
		except:
			i["pages"]=''

	auth_dict=get_list_of_dict(eledict,"author",xp_author)
	for i in auth_dict:
		i["full_name"]=i['fname']+'/'+i["mname"]+'/'+i['lname']
	jour_dict=get_list_of_dict(eledict,"submission_path",xp_journal,dbv=db_journal)

	fid_dict=get_list_of_dict(eledict,"field",xp_field)

	key_dict=get_list_of_dict(eledict,"keyword",xp_keyword)
	for i in key_dict:
		for j in i.keys():
			if j=='':
				i["keyword"]=i[j]
				i.pop(j)

	return dict(zip(["Document","Author","Journal","Field","Keyword"],[doc_dict, auth_dict, jour_dict, fid_dict, key_dict]))
            















