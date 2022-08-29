import config
import codaio
import logging

log = logging.getLogger(__name__)


settings = config.Settings()
coda = config.CodaClient(settings)

# TODO: 
#  1) Query on tables
#  2) Write new rows

for table in coda.doc.list_tables():

    print(f'{table}')

    if table.name == "Projects":

        for row in coda.get_rows(table):
            print(row)
