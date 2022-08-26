import requests
import os
import config

class Row(object):

    def __init__(self, item_dict, columns):

        self.id = item_dict['id']
        self.values = {}
        for key, value in item_dict['values'].items():

            self.values[key] = value

    def __str__(self):

        return f'[{self.id}] {self.values}'

class Column(object):

    def __init__(self,item_dict):
        self.id = item_dict['id']
        self.name = item_dict['name']

    def __str__(self):

        return f'{self.name} [{self.id}]'

class Table(object):

    def __init__(self,item_dict):

        self.CODA_TABLE_ID = item_dict['id']
        self.name = item_dict['name']
        self.columns = self.columns_get()

    def __str__(self):

        return f'{self.name} [{self.CODA_TABLE_ID}]'

    def rows_get(self):

        uri = f"https://coda.io/apis/v1/docs/{config.CODA_DOC_ID}/tables/{self.CODA_TABLE_ID}/rows"
        req = requests.get(uri, headers=config.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        return [Row(item_i, self.columns) for item_i in req.json()['items']]

    def columns_get(self):

        uri = f"https://coda.io/apis/v1/docs/{config.CODA_DOC_ID}/tables/{self.CODA_TABLE_ID}/columns"
        req = requests.get(uri, headers=config.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        return [Column(item_i) for item_i in req.json()['items']]


class Client(object):

    def __init__(self):

        self.tables = self.tables_get()

    def tables_get(self):

        uri = f"https://coda.io/apis/v1/docs/{config.CODA_DOC_ID}/tables"
        req = requests.get(uri, headers=config.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        return [Table(item_i) for item_i in req.json()['items']]


coda = Client()

for table in coda.tables:

    if table.name == "Slack Users":

        print(table)
        for column in table.columns:
            print(f"   {column}")

        for row in table.rows_get():
            print(row)
