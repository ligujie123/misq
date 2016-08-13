import os
from pipeline import pipeline
from models import db_connect, create_table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = db_connect(os.getcwd())
create_table(engine)
Session = sessionmaker(bind=engine)
session = Session()

#generate every files absolute path
def generate_path(rootpath):
    for dirpath, dirnames, filenames in os.walk(rootpath):
        for filename in filenames:
            if ".xml" in filename:
                if "._" not in filename:
                    yield os.path.join(dirpath,filename)

rootpath=os.getcwd()+'/misq'
xmlpath=generate_path(rootpath)



def main():
    i = 0 
    n = 0
    for fp in xmlpath:
        try:
            i += 1
            pipeline(fp,session)
        except:
            n += 1
            print("Failed filename: ", fp)
    session.commit()
    session.close()
    print("Number of Total Failed Files: ", n)
    print("Number of Total Successful Files: ", i)

if __name__=="__main__":
    main()



    