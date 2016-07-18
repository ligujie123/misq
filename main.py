import os
from pipeline import pipeline
from models import db_connect, create_table
from sqlalchemy.orm import sessionmaker

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
	for fp in xmlpath:
		try:
			pipeline(fp,session)
		except:
			pass
	

if __name__=="__main__":
	main()

		


