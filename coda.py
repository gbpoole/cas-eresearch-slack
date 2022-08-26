import requests
import os

class Client(object):

    CODA_API_TOKEN = os.environ['CODA_TOKEN']
    CODA_DOC_ID = "3zs35nY4oB"
    headers = {'Authorization': f"Bearer {CODA_API_TOKEN}"}

    def __init__(self):

        pass

    def tables_get(self):

        uri = f"https://coda.io/apis/v1/docs/{self.CODA_DOC_ID}/tables"

        req = requests.get(uri, headers=self.headers)
        req.raise_for_status() # Throw if there was an error.
        return [{'name':req_i['name'],'id':req_i['id']} for req_i in req.json()['items']]

    def rows_get(self, CODA_TABLE_ID, CODA_COLUMN_ID, CODA_COLUMN_QUERY):

        uri = f"https://coda.io/apis/v1/docs/{self.CODA_DOC_ID}/tables/{CODA_TABLE_ID}/rows"

        params = {
          f'query': f'{CODA_COLUMN_ID}:"{CODA_COLUMN_QUERY}"',
        }

        req = requests.get(uri, headers=self.headers, params=params)
        req.raise_for_status() # Throw if there was an error.
        return req.json()

client = Client()

tables = client.tables_get()

for table in tables:
    print(table)
