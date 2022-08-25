import requests
import os

CODA_API_TOKEN = os.environ['CODA_TOKEN']
CODA_DOC_ID = "3zs35nY4oB"
CODA_TABLE_ID = "grid-Az0iVvW7sF"
CODA_COLUMN_ID = "c-1lLiKSk3uP"
CODA_COLUMN_QUERY = "Jes"

headers = {'Authorization': f"Bearer {CODA_API_TOKEN}"}
uri = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}/tables/{CODA_TABLE_ID}/rows"
print(headers)
print(uri)

params = {
  f'query': f'{CODA_COLUMN_ID}:"{CODA_COLUMN_QUERY}"',
}
print(params)
req = requests.get(uri, headers=headers, params=params)
req.raise_for_status() # Throw if there was an error.
res = req.json()

print(f'Matching rows: {len(res["items"])}')
print(res)

#  uri = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}"
#  res = requests.get(uri, headers=headers).json()
#  print(uri)
#  print(res)
