# misq

#_______in terminal mode_____
1 from the ternminal, clone the whole file through git.
 
2 cd on the direcotry misq2, choose venv_osx as the virtual env.
 (which includes sqlalchemy and lxml)

3 open python in terminal
 
#_________in python mode______

4 >>>from main import * 
 #which includes main(), session

5 >>>main()
 #the data.sqlite will be created. its size is about 15kb
 
6 >>>from models import *
 #which contains the models such as Document(the papers), Author(authors), Keywords, Field(the attributes for this document) and Journal.
 
7 >>>session.query(Document).count()
1300 #some number like this 
  
8 >>>session.query(Author).count()
800#some number like this.
 #you can check more information about this database through session.
 
9 >>>session.close()
 #close the session 
