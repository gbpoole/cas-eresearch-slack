from logging import getLogger
from codaio import Coda, Document, Cell
from functools import lru_cache
from fastapi import Depends
import app.config

log = getLogger(__name__)


class CodaClient(object):

    def __init__(self, settings):

    	self.client = Coda(settings.CODA_API_TOKEN)
    	self.doc    = Document(settings.CODA_DOC_ID, coda=self.client)

    	# Fetch the metadata for the tables that we will need
    	table_aliases = {
    	    'People':            'people',
    	    'Slack Users':       'slack_users',
    	    'Slack Channels':    'slack_channels',
    	    'Projects':          'projects',
    	    'Timesheet Entries': 'timesheet',
    	}
    	self.tables = {}
    	tables = self.doc.list_tables()
    	for table in tables:
    	    if table.name in table_aliases.keys():
    	        self.tables[table_aliases[table.name]]=table

    def get_rows(self, table_alias, query=None):

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
def get_client(settings: app.config.Settings) -> CodaClient:
    log.info("Initialising Coda client...")
    return CodaClient(settings)
