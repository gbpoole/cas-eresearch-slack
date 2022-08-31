from logging import getLogger
from codaio import Coda, Document, Cell
from functools import lru_cache
from fastapi import Depends
import config

log = getLogger(__name__)


class CodaClient(object):

    def __init__(self,settings: config.Settings):

        self.client = Coda(settings.CODA_API_TOKEN)
        self.doc    = Document(settings.CODA_DOC_ID, coda=self.client)
        self.settings = settings

        # Fetch the metadata for the tables that we will need
        table_alias_list = {
            'People':            'people',
            'Slack Users':       'slack',
            'Projects':          'projects',
            'Timesheet Entries': 'timesheet',
        }
        self.tables = {}
        tables = self.doc.list_tables()
        for table in tables:
            if table.name in table_alias_list.keys():
                self.tables[table_alias_list[table.name]]=table

    def get_rows(self, table_alias, query):

        results = []
        for row in self.client.list_rows(self.doc.id, self.tables[table_alias].id, use_column_names=True, query=query)['items']:
            result = {}
            for key, value in row['values'].items():
                result[key]=value
            results.append(result)

        return results

    def put_rows(self, table_alias, data_in):

        rows = []
        for data_i in data_in:
            row = []
            for key, value in data_i.items():
                row.append(Cell(column=key,value_storage=value))
            rows.append(row)

        self.tables[table_alias].upsert_rows(rows)

        return

@lru_cache()
def init_client(settings: config.Settings = Depends(config.get_settings)) -> object:
    log.info("Initialising Coda client...")
    return CodaClient(settings)
