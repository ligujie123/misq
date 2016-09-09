
# From XLMfile to Database
    This tutorial will illustrate the main processes of extracting raw data from XML file to Database.
    
    The main processes and corresponding python files are as follows:
    
    
1. `parse.py`: __extract__ raw data from a __XML file__ to a __dictionary__.
2. `models.py`: __construct__ database models to store the data.
3. `pipeline.py`: __establish__ a pipeline to transfer dictionary data to database.
4. `main.py`: __connect__ database, __walk__ through directory, __report__ information.
    



> For the whole project, in order to get database
>
> you can run main.py in the terminal
>
> then, you will get file `data.sqlite`



``` shell
$ cd /Users/floyd/Projects/misq

$ python main.py

Failed filename:/Users/floyd/Projects/misq/misq/vol31/iss1/2/0-MISQPodcast.xml
Number of Total Failed Files:  1
Number of Total Successful Files:  1307

```



## 1. parse.py: extract raw data from XML file to dictionary.

__Main points to cover__

1. XML data structure: metadata.xml

2. Using lxml to parse XML file

3. `xpv`, `dbv` and `xpv2dbv()`

4. From file to blocks

5. From block to elements: `block2ele()`

6. Handling special cases and return dictionary: `parseXML2dict()`

7. Tests



### 1 Here we use this file as an example

`/Users/floyd/Projects/misq/misq/vol40/iss1/13/metadata.xml`

![metadata](http://a1.qpic.cn/psb?/V13CYERa0jEWMD/XAfP61KkfxcKJkb6ru3vHcqNl531xyCZuqwQ1h0eOMw!/m/dPgAAAAAAAAA&bo=8gJ.AQAAAAADB60!&rf=photolist)


From the graph, after analyzing the structure of this data file, we will construct five tables.

documents, authors, keywords, journals, fields

The columns in each Table

documents


```python
#generate absolute path
path1 = "/Users/floyd/Projects/misq/misq/vol40/iss1/13/metadata.xml"
```

    We use lxml to extract element in the XML file.
    


```python
# First we use etree which is from lxml to parse the whole XML file
# Then we get an ElementTree, which contains all the information in this XML file
from lxml import etree
tree = etree.parse(path1)
tree
```




    <lxml.etree._ElementTree at 0x1045667c8>



### 2 We get `tree` from etree(), which has a method `xpath()`. 

`xpath()` needs __xpaths__ as arguments then return a __list__ of elements

For how xpath works, check http://www.w3.org/TR/xpath/


```python
# this is an example
xp = ".//author"
auths = tree.xpath(xp)
auths
```




    [<Element author at 0x104572248>,
     <Element author at 0x104572288>,
     <Element author at 0x1045722c8>]




```python
type(auths)
```




    list



#### 3 from xpv to dbv

`xpv` means xpath variables, which is used to extract elements from ElementTree.

`dbv` means database variables, which would be used as dictionary keys and database columns

We will use function `xpv2dbv()` to get `dbv` from `xpv`.


```python
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
```


```python
# here is a special table: journal table
# because we cannot get dbv_journal from xpv_journal by the function I will introduce soon.
xpv_journal = ["text()"]

dbv_journal = ["domain", 
               "vol", 
               "iss", 
               "label"]
```

In order to get the dbv which is neat enought to act as dictionary keys or database column labels

we need a function to strip 'text()', '@', '.' and replace '-' with '_'.


```python
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
```


```python
# test this function
dbv_document = xpv2dbv(xpv_document)
xpv_document
```




    ['title/text()',
     'abstract/text()',
     'publication-title/text()',
     'publication-date/text()',
     'submission-date/text()',
     'coverpage-url/text()',
     'fulltext-url/text()',
     'fpage/text()',
     'lpage/text()',
     'document-type/text()',
     'type/text()',
     'articleid/text()',
     'context-key/text()',
     'submission-path/text()',
     'label/text()']



#### 4  from file to blocks
We need five tables, therefore, we need to divide the file into five blocks where each block represents a table


```python
# Illustration of the way from file to blocks

path1 = "/Users/floyd/Projects/misq/misq/vol40/iss1/13/metadata.xml"
# get ElementTree
tree = etree.parse(path1)

# as shown above, the xpv_blocks is a list of xpaths.
xpv_blocks = [".//document", 
              ".//author",
              ".//keyword",
              ".//field",
              ".//submission-path"]
    
dbv_blocks = xpv2dbv(xpv_blocks)

#have a look at this list
dbv_blocks
```




    ['document', 'author', 'keyword', 'field', 'submission_path']




```python
tree.xpath('.//keyword')
```




    [<Element keyword at 0x104584f08>,
     <Element keyword at 0x104584f88>,
     <Element keyword at 0x104584fc8>,
     <Element keyword at 0x10456b048>,
     <Element keyword at 0x10456bd88>]




```python
# using functional programming to get a list.
tree = etree.parse(path1)

# we also add list() before map, because map will return a generator.
blockslist = list(map(tree.xpath, xpv_blocks))
blockslist
```




    [[<Element document at 0x10456bf48>],
     [<Element author at 0x10456bf88>,
      <Element author at 0x10456bfc8>,
      <Element author at 0x104589048>],
     [<Element keyword at 0x104589088>,
      <Element keyword at 0x1045890c8>,
      <Element keyword at 0x104589108>,
      <Element keyword at 0x104589148>,
      <Element keyword at 0x104589188>],
     [<Element field at 0x1045891c8>,
      <Element field at 0x104589208>,
      <Element field at 0x104589248>,
      <Element field at 0x104589288>],
     [<Element submission-path at 0x1045892c8>]]




```python
# get dictionary of blocks

blocksdict = dict(zip(dbv_blocks, blockslist))

#show blocksdict
blocksdict
```




    {'author': [<Element author at 0x10456bf88>,
      <Element author at 0x10456bfc8>,
      <Element author at 0x104589048>],
     'document': [<Element document at 0x10456bf48>],
     'field': [<Element field at 0x1045891c8>,
      <Element field at 0x104589208>,
      <Element field at 0x104589248>,
      <Element field at 0x104589288>],
     'keyword': [<Element keyword at 0x104589088>,
      <Element keyword at 0x1045890c8>,
      <Element keyword at 0x104589108>,
      <Element keyword at 0x104589148>,
      <Element keyword at 0x104589188>],
     'submission_path': [<Element submission-path at 0x1045892c8>]}



#### 5 from blocks to elements

We got a dictionary -- blocksdict.

For each pair of key and value

Key is table label, value is table blocks. More specifically, values are lists of elements for each table.

What we should do is turn the element to a dictionary with keys from dbv list.


```python
# take author as example

auth_table = blocksdict['author']
# then we get a list of element
auth_table
```




    [<Element author at 0x10456bf88>,
     <Element author at 0x10456bfc8>,
     <Element author at 0x104589048>]




```python
# get an element
auth1 = auth_table[0]
auth1
```




    <Element author at 0x10456bf88>




```python
authlist = list(map(auth1.xpath, xpv_author))
authlist
```




    [['Jie Mein'], [], ['Goh'], ['jmgoh@sfu.ca'], ['Simon Fraser University']]




```python
for i in range(len(authlist)):
    tem = authlist[i]
    try:
        authlist[i] = tem[0]
    except:
        authlist[i] = ''
authlist
```




    ['Jie Mein', '', 'Goh', 'jmgoh@sfu.ca', 'Simon Fraser University']




```python
auth1dict = dict(zip(xpv2dbv(xpv_author), authlist))
auth1dict
```




    {'email': 'jmgoh@sfu.ca',
     'fname': 'Jie Mein',
     'institution': 'Simon Fraser University',
     'lname': 'Goh',
     'mname': ''}




```python
# input

print(type(auth1))
auth1
```

    <class 'lxml.etree._Element'>





    <Element author at 0x10456bf88>




```python
# output

print(type(auth1dict))
auth1dict
```

    <class 'dict'>





    {'email': 'jmgoh@sfu.ca',
     'fname': 'Jie Mein',
     'institution': 'Simon Fraser University',
     'lname': 'Goh',
     'mname': ''}



Folliwing this logic, we can design a function to transfer Element to dictionary.




```python
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
    
```

#### Handling special cases

among these five tables, some special things needed to be handled.

1 `journal` table: unique to other fours. To get element dictionary, we need to extract from the element "submission-path"




```python
# the four arguments

# when key == "submission_path"
# xpv = xpv_journal


blocksdict = blocksdict
key = "submission_path"
xpv = xpv_journal
dbv = dbv_journal # which is define at very first part. 
print(key, xpv, dbv)
```

    submission_path ['text()'] ['domain', 'vol', 'iss', 'label']



```python
# ele is the first element in the list
dictlist = []
ele = blocksdict[key][0]
# xpv is a list
raw = ele.xpath(xpv[0]) 
elelist = raw[0].split('/')
dictlist.append(dict((zip(dbv, elelist))))
dictlist
```




    [{'domain': 'misq', 'iss': 'iss1', 'label': '13', 'vol': 'vol40'}]



2 other tables: need to add some other column labels
+ document: pages = lpage - fpage + 1
+ author: full name = fname + '/' + mname + '/' + 'lname'
+ keyword: change element dictionary's keys from '' to 'keyword'


```python
#generate the diclist

# document_dictlist
doc_dict = ele2dictlist(blocksdict,"document",xpv_document)
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

dict(zip(["Document","Author","Journal","Field","Keyword"],[doc_dict, auth_dict, jour_dict, fid_dict, key_dict]))
```




    {'Author': [{'email': 'jmgoh@sfu.ca',
       'fname': 'Jie Mein',
       'full_name': 'Jie Mein//Goh',
       'institution': 'Simon Fraser University',
       'lname': 'Goh',
       'mname': ''},
      {'email': 'ggao@rhsmith.umd.edu',
       'fname': 'Guodong',
       'full_name': 'Guodong/(Gordon)/Gao',
       'institution': 'University of Maryland - College Park',
       'lname': 'Gao',
       'mname': '(Gordon)'},
      {'email': 'ragarwal@rhsmith.umd.edu',
       'fname': 'Ritu',
       'full_name': 'Ritu//Agarwal',
       'institution': 'University of Maryland',
       'lname': 'Agarwal',
       'mname': ''}],
     'Document': [{'abstract': '<p><em>The striking growth of online communities in recent years has sparked significant interest in understanding and quantifying benefits of participation. While research has begun to document the economic outcomes associated with online communities, quantifying the social value created in these collectives has been largely overlooked. This study proposes that online health communities create social value by addressing ruralâ\x80\x93urban health disparities via improved health capabilities. Using a unique data set from a rare disease community, we provide one of the first empirical studies of social value creation. Our quantitative analysis using exponential random graph models reveals patterns of social support exchanged between users and the variations in these patterns based on usersâ\x80\x99 location. We find that, overall, urban users are net suppliers of social support while rural participants are net recipients, suggesting that technology-mediated online health communities are able to alleviate ruralâ\x80\x93urban health disparities. This study advances extant understanding of value production in online collectives, and yields implications for policy. </em></p>',
       'articleid': '3281',
       'context_key': '8235621',
       'coverpage_url': 'http://aisel.aisnet.org/misq/vol40/iss1/13',
       'document_type': 'article',
       'fpage': '247',
       'fulltext_url': 'http://aisel.aisnet.org/cgi/viewcontent.cgi?article=3281&amp;context=misq&amp;unstamped=1',
       'label': '13',
       'lpage': '263',
       'pages': '17',
       'publication_date': '2016-03-01T00:00:00-08:00',
       'publication_title': 'Management Information Systems Quarterly',
       'submission_date': '2016-02-29T08:26:26-08:00',
       'submission_path': 'misq/vol40/iss1/13',
       'title': 'The Creation of Social Value:  Can an Online Health Community Reduce Rural-Urban Health Disparities?',
       'type': 'article'}],
     'Field': [{'name': 'embargo_date',
       'type': 'date',
       'value': '2016-02-29T00:00:00-08:00'},
      {'name': 'peer_reviewed', 'type': 'boolean', 'value': 'true'},
      {'name': 'publication_date',
       'type': 'date',
       'value': '2016-03-01T00:00:00-08:00'},
      {'name': 'short_title',
       'type': 'string',
       'value': '/Creation of Social Value with Online Health Communities'}],
     'Journal': [{'domain': 'misq', 'iss': 'iss1', 'label': '13', 'vol': 'vol40'}],
     'Keyword': [{'keyword': 'Healthcare'},
      {'keyword': 'online communities'},
      {'keyword': 'social value'},
      {'keyword': 'disparities'},
      {'keyword': 'social network'}]}




```python
# compare with blocksdict
blocksdict
```




    {'author': [<Element author at 0x10456bf88>,
      <Element author at 0x10456bfc8>,
      <Element author at 0x104589048>],
     'document': [<Element document at 0x10456bf48>],
     'field': [<Element field at 0x1045891c8>,
      <Element field at 0x104589208>,
      <Element field at 0x104589248>,
      <Element field at 0x104589288>],
     'keyword': [<Element keyword at 0x104589088>,
      <Element keyword at 0x1045890c8>,
      <Element keyword at 0x104589108>,
      <Element keyword at 0x104589148>,
      <Element keyword at 0x104589188>],
     'submission_path': [<Element submission-path at 0x1045892c8>]}



#### 6 final function: parseXML2dict( )


```python
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
```

### testing


```python
path1
```




    '/Users/floyd/Projects/misq/misq/vol40/iss1/13/metadata.xml'




```python
parseXML2dict(path1)
```




    {'Author': [{'email': 'jmgoh@sfu.ca',
       'fname': 'Jie Mein',
       'full_name': 'Jie Mein//Goh',
       'institution': 'Simon Fraser University',
       'lname': 'Goh',
       'mname': ''},
      {'email': 'ggao@rhsmith.umd.edu',
       'fname': 'Guodong',
       'full_name': 'Guodong/(Gordon)/Gao',
       'institution': 'University of Maryland - College Park',
       'lname': 'Gao',
       'mname': '(Gordon)'},
      {'email': 'ragarwal@rhsmith.umd.edu',
       'fname': 'Ritu',
       'full_name': 'Ritu//Agarwal',
       'institution': 'University of Maryland',
       'lname': 'Agarwal',
       'mname': ''}],
     'Document': [{'abstract': '<p><em>The striking growth of online communities in recent years has sparked significant interest in understanding and quantifying benefits of participation. While research has begun to document the economic outcomes associated with online communities, quantifying the social value created in these collectives has been largely overlooked. This study proposes that online health communities create social value by addressing ruralâ\x80\x93urban health disparities via improved health capabilities. Using a unique data set from a rare disease community, we provide one of the first empirical studies of social value creation. Our quantitative analysis using exponential random graph models reveals patterns of social support exchanged between users and the variations in these patterns based on usersâ\x80\x99 location. We find that, overall, urban users are net suppliers of social support while rural participants are net recipients, suggesting that technology-mediated online health communities are able to alleviate ruralâ\x80\x93urban health disparities. This study advances extant understanding of value production in online collectives, and yields implications for policy. </em></p>',
       'articleid': '3281',
       'context_key': '8235621',
       'coverpage_url': 'http://aisel.aisnet.org/misq/vol40/iss1/13',
       'document_type': 'article',
       'fpage': '247',
       'fulltext_url': 'http://aisel.aisnet.org/cgi/viewcontent.cgi?article=3281&amp;context=misq&amp;unstamped=1',
       'label': '13',
       'lpage': '263',
       'pages': '17',
       'publication_date': '2016-03-01T00:00:00-08:00',
       'publication_title': 'Management Information Systems Quarterly',
       'submission_date': '2016-02-29T08:26:26-08:00',
       'submission_path': 'misq/vol40/iss1/13',
       'title': 'The Creation of Social Value:  Can an Online Health Community Reduce Rural-Urban Health Disparities?',
       'type': 'article'}],
     'Field': [{'name': 'embargo_date',
       'type': 'date',
       'value': '2016-02-29T00:00:00-08:00'},
      {'name': 'peer_reviewed', 'type': 'boolean', 'value': 'true'},
      {'name': 'publication_date',
       'type': 'date',
       'value': '2016-03-01T00:00:00-08:00'},
      {'name': 'short_title',
       'type': 'string',
       'value': '/Creation of Social Value with Online Health Communities'}],
     'Journal': [{'domain': 'misq', 'iss': 'iss1', 'label': '13', 'vol': 'vol40'}],
     'Keyword': [{'keyword': 'Healthcare'},
      {'keyword': 'online communities'},
      {'keyword': 'social value'},
      {'keyword': 'disparities'},
      {'keyword': 'social network'}]}




```python
# change path1
path2 = '/Users/floyd/Projects/misq/misq/vol39/iss1/13/metadata.xml'
```


```python
parseXML2dict(path2)
```




    {'Author': [{'email': 'be.itm@cbs.dk',
       'fname': 'Ben',
       'full_name': 'Ben//Eaton',
       'institution': 'Copenhagen Business School',
       'lname': 'Eaton',
       'mname': ''},
      {'email': 'S.M.Elaluf-Calderwood@lse.ac.uk',
       'fname': 'Silvia',
       'full_name': 'Silvia//Elaluf-Calderwood',
       'institution': 'London School of Economics and Political Science',
       'lname': 'Elaluf-Calderwood',
       'mname': ''},
      {'email': 'c.sorensen@lse.ac.uk',
       'fname': 'Carsten',
       'full_name': 'Carsten//Sorensen',
       'institution': 'London School of Economics and Political Science',
       'lname': 'Sorensen',
       'mname': ''},
      {'email': 'youngjin.yoo@temple.edu',
       'fname': 'Youngjin',
       'full_name': 'Youngjin//Yoo',
       'institution': '',
       'lname': 'Yoo',
       'mname': ''}],
     'Document': [{'abstract': '<p><em>The digital age has seen the rise of service systems involving highly distributed, heterogeneous, and resource-integrating actors whose relationships are governed by shared institutional logics, standards, and digital technology. The cocreation of service within these service systems takes place in the context of a paradoxical tension between the logic of generative and democratic innovations and the logic of infrastructural control. Boundary resources play a critical role in managing the tension as a firm that owns the infrastructure can secure its control over the service system while independent firms can participate in the service system. In this study, we explore the evolution of boundary resources. Drawing on Pickeringâ\x80\x99s (1993) and Barrett et al.â\x80\x99s (2012) conceptualizations of tuning, the paper seeks to forward our understanding of how heterogeneous actors engage in the tuning of boundary resources within Appleâ\x80\x99s iOS service system. We conduct an embedded case study of Appleâ\x80\x99s iOS service system with an in-depth analysis of 4,664 blog articles concerned with 30 boundary resources covering 6 distinct themes. Our analysis reveals that boundary resources of service systems enabled by digital technology are shaped and reshaped through distributed tuning, which involves cascading actions of accommodations and rejections of a network of heterogeneous actors and artifacts. Our study also shows the dualistic role of power in the distributed tuning process.</em></p>',
       'articleid': '3229',
       'context_key': '6759459',
       'coverpage_url': 'http://aisel.aisnet.org/misq/vol39/iss1/13',
       'document_type': 'article',
       'fpage': '217',
       'fulltext_url': 'http://aisel.aisnet.org/cgi/viewcontent.cgi?article=3229&amp;context=misq&amp;unstamped=1',
       'label': '13',
       'lpage': '243',
       'pages': '27',
       'publication_date': '2015-03-01T00:00:00-08:00',
       'publication_title': 'Management Information Systems Quarterly',
       'submission_date': '2015-03-02T12:13:08-08:00',
       'submission_path': 'misq/vol39/iss1/13',
       'title': "Distributed Tuning of Boundary Resources:  The Case of Apple's iOS Service System",
       'type': 'article'}],
     'Field': [{'name': 'embargo_date',
       'type': 'date',
       'value': '2015-03-02T00:00:00-08:00'},
      {'name': 'peer_reviewed', 'type': 'boolean', 'value': 'true'},
      {'name': 'publication_date',
       'type': 'date',
       'value': '2015-03-01T00:00:00-08:00'},
      {'name': 'short_title',
       'type': 'string',
       'value': 'Distributed Tuning of Boundary Resources'}],
     'Journal': [{'domain': 'misq', 'iss': 'iss1', 'label': '13', 'vol': 'vol39'}],
     'Keyword': [{'keyword': 'Service system innovation'},
      {'keyword': 'mobile platform'},
      {'keyword': 'ecosystem'},
      {'keyword': 'digital infrastructure'},
      {'keyword': 'boundary resource dynamics'},
      {'keyword': 'tuning'},
      {'keyword': 'sociomateriality'},
      {'keyword': 'iOS'}]}




```python
path3 = '/Users/floyd/Projects/misq/misq/vol1/iss1/1/metadata.xml'
```


```python
parseXML2dict(path3)
```




    {'Author': [{'email': '',
       'fname': 'Gerald',
       'full_name': 'Gerald//Matlin',
       'institution': '',
       'lname': 'Matlin',
       'mname': ''}],
     'Document': [{'abstract': '',
       'articleid': '1801',
       'context_key': '583177',
       'coverpage_url': 'http://aisel.aisnet.org/misq/vol1/iss1/1',
       'document_type': 'article',
       'fpage': '',
       'fulltext_url': 'http://aisel.aisnet.org/cgi/viewcontent.cgi?article=1801&amp;context=misq&amp;unstamped=1',
       'label': '1',
       'lpage': '',
       'pages': '',
       'publication_date': '1977-12-31T00:00:00-08:00',
       'publication_title': 'Management Information Systems Quarterly',
       'submission_date': '2008-08-18T07:00:03-07:00',
       'submission_path': 'misq/vol1/iss1/1',
       'title': 'How to Survive a Management Assessment',
       'type': 'article'}],
     'Field': [{'name': 'peer_reviewed', 'type': 'boolean', 'value': 'true'},
      {'name': 'publication_date',
       'type': 'date',
       'value': '1977-12-31T00:00:00-08:00'}],
     'Journal': [{'domain': 'misq', 'iss': 'iss1', 'label': '1', 'vol': 'vol1'}],
     'Keyword': []}




```python

```


```python

```

## 2. `Models.py`: construct database models to store the data

This part's focus is how to use sqlalchemy to construct database models.

For further information about `sqlalchemy`, visit: http://docs.sqlalchemy.org/en/latest/

And this tutorial uses `sqlite3` instead of `MySQL` or `PostgreSQL`.

These models will be the containers which store the dictionary returned by function `parseXML2dict()`.

Two main sections:

1. Building basic mapping table classes
2. Building relationships




### 1 Building basic mapping table classes

Import the needed packages or methods.


```python
# to get the database's absolute path.
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# for building the basic mapping table classes.
from sqlalchemy import Column, String, Integer, Table

# for building relationships among tables.
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

```

Define the function to create connection with database and to create essential table class


```python
# create_engine need database URI as the augument.
# sqlite3's URI form (for Mac) is such: 'sqlite:////absolute/path/to/database'
def db_connect(basedir):
    return create_engine('sqlite:///'+os.path.join(basedir, 'data.sqlite'))

# we get Base from the initializaiton of class declarative_base
# Base will be the basic table which will be extended to other tables
# then we connect this basic table to the engine.
Base= declarative_base()
def create_table(engine):
    Base.metadata.create_all(engine)
```

Construct table classes

```python

# let's first take document table class as an example
class Document(Base):
    # the tablename in Database
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
    
    
    def __repr__(self):
        return "<Document(title=%r)>" %self.title
    
    
# essentially, every column label is from list: dbv_documents.

# other table classes follow the same pattern

```

### 2 Construct relationships between tables.

We must notice that there are relationships between tables

> __One to One__:
>
> For `documents` and `journal`, there is a one to one relationship
>
> (journal's entry is generated from document's submission_path)
>
>
> __One to Many__:
>
> There exits one to many relationship.
>
> Take a classes table and a students table for instance.
>
> A class will have many students who are in this class.
>
> A student will only have one class generally.
>
> So this is a one to many relationship.
>
>
> __Many to Many__:
>
> For many to many relationship, take this example
>
> A courses table and a students table
>
> A course will have many students who attend this course
>
> And a student will have many courses for the courses he or she attends.


And will have many "m:m" relationships here:
+ documents : authors
+ documents : keywords
+ documents : fields

It is true that between `authors` table and `keyword` table, there are also a m:m relationship between them.

However, we can achieve this by using the SQL language.

So, to make life easy, we do not establish this relationship in `models.py`.



##### Take documents and authors tables as example.

```python

# we create an register table here.
# this table has two columns: 'documents_id' and 'authors_id'

documents_authors = Table('documents_authors', Base.metadata,
                          Column('documents_id', ForeignKey("documents.id"), primary_key=True),
                          Column('authors_id', ForeignKey("authors.id"), primary_key=True))

class Document(Base):
    #### This part is not change, is the same as above ####
    __tablename__='documents'

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
    
    def __repr__(self):
        return "<Document(title=%r)>" %self.title

    
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
        
```


Following this pattern, we can draw the whole `models.py`.

## 3 `pipeline.py`: transfer dictionary data to database

We first combine the database, and then create the session.

and we use `parseXML2dict()` here.



```python
from models import Document, Author, Keyword, Field, Journal
```


```python
type(parseXML2dict)
```




    function




```python
# using an easy name.
par = parseXML2dict
```

#### Transfer entries to the database


```python

# take absolute path and session as input
# return nothing
# but add all the entries to the database session

def pipeline(abspath,session):
    
    #par() is parseXML2dict() imported from parse.py
    d = par(abspath)
    
    # d["Document"] is a list of dictionary
    # as there is only one dict in this list.
    # so by d['Document'][0]
    # we directly get a document_dictionary: doc. 
    
    doc = d["Document"][0]
    
    # the argument **doc is keyword argument.
    # we initialize Document with dictionary: doc
    # then we get a model object doc_t
    doc_t = Document(**doc)

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


```

## 4 `main.py`

This module will do this three main things:

1. Connecting to database
2. Walking through the directory
3. Reporting the information

### 1 Connecting to database


```python
import os

# input function pipeline()
from pipeline import pipeline

# input database related methods
from models import db_connect, create_table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


```


```python
os.getcwd()
```




    '/Users/floyd/Projects/misq'




```python
engine = db_connect(os.getcwd())
create_table(engine)
Session = sessionmaker(bind=engine)
session = Session()
```

### 2 Walking through directory


```python
# here we use os.walk to try to get all the xml file absolute path.

def generate_path(rootpath):
    for dirpath, dirnames, filenames in os.walk(rootpath):
        for filename in filenames:
            if ".xml" in filename:
                if "._" not in filename:
                    yield os.path.join(dirpath,filename)
```


```python
rootpath=os.getcwd()+'/misq'
rootpath
```




    '/Users/floyd/Projects/misq/misq'




```python
xmlpath=generate_path(rootpath)
```


```python
# xlmpath is a generator.
type(xmlpath)
```




    generator




```python
for i in xmlpath:
    print(i)
```

    /Users/floyd/Projects/misq/misq/vol1/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol1/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol10/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol11/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/20/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol12/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol13/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol14/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol15/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol16/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol17/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol18/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol19/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol2/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol20/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol21/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol22/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol23/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol24/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol25/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol26/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol27/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol28/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol29/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol3/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol30/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/2/0-MISQPodcast.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol31/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol32/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol33/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol34/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/20/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol35/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/20/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/21/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/22/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol36/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/18/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/19/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/20/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/21/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/22/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/23/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol37/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/15/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/16/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/17/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol38/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/14/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss2/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss3/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol39/iss4/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol4/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/10/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/11/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/12/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/13/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/7/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/8/metadata.xml
    /Users/floyd/Projects/misq/misq/vol40/iss1/9/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol5/iss4/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol6/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol7/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol8/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss1/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss2/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss3/6/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/1/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/2/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/3/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/4/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/5/metadata.xml
    /Users/floyd/Projects/misq/misq/vol9/iss4/6/metadata.xml


### 3 Report information and transfer all data to Database


```python
xmlpath = generate_path(rootpath)

i = 0
n = 0
for fp in xmlpath:
    try:
        i += 1
        pipeline(fp,session)
    except:
        n += 1
        print("Failed filename: ",fp)
session.commit()
session.close()
print("Number of Total Failed Files: ",n)
print("Number of Total Successful Files: ", i)
```

    Failed filename:  /Users/floyd/Projects/misq/misq/vol31/iss1/2/0-MISQPodcast.xml
    Number of Total Failed Files:  1
    Number of Total Successful Files:  1307



```python

```
