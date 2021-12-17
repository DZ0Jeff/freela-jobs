from sqlalchemy import create_engine, Column, Integer, Text, MetaData, Table, select
from sqlalchemy.exc import OperationalError

class DataStorage:
    def __init__(self) -> None:    
        self.engine = create_engine('postgresql://imlrjrjn:vICfrIZh6wFCncLdVmcH5akVTgxzyJSh@kesavan.db.elephantsql.com/imlrjrjn')
        self.create_table()


    def create_table(self):
        try:
            metadata = MetaData()
            self.jobs_schema = Table(
                'jobs', metadata,
                Column('id', Integer, primary_key=True),
                Column('title', Text),
                Column('link', Text),
                Column('client', Text),
                Column('description', Text),
            )

            self.jobs_schema.create(bind=self.engine, checkfirst=True)
        
        except OperationalError as error:
            print('> Erro ao conectar ao banco de dados!')
            print(error)
            return

    def insert(self, title, link, client, description):
        insert_message = self.jobs_schema.insert().values(title=title, link=link, client=client, description=description)
        self.engine.execute(insert_message)

    def select_by_link(self):
        stmt = select([self.jobs_schema.c.link]) 
        message = self.engine.execute(stmt).fetchall()
        return message 

    def select_by_name(self):
        stmt = select([self.jobs_schema.c.title]) 
        message = self.engine.execute(stmt).fetchall()
        return message 
