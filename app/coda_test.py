import requests
import os
import config
from typing import Optional
from functools import lru_cache
from fastapi import Depends
from pydantic import BaseModel, BaseSettings, Field, HttpUrl, constr, ValidationError
import logging

log = logging.getLogger(__name__)

class Row(BaseModel):

    def __init__(self, item_dict, columns):

        self.id = item_dict['id']
        self.values = {}
        for key, value in item_dict['values'].items():

            self.values[key] = value

    def __str__(self):

        return f'[{self.id}] {self.values}'

class ColumnFormat(BaseModel):
    id_: str = Field(alias='id')
    type_: constr(regex='column') = Field(alias='type')
    name: str
    href: HttpUrl


class Column(BaseModel):

    id_: str = Field(alias='id')
    type_: str = Field(alias='type')
    name: str
    href: HttpUrl
    format_: Optional[ColumnFormat] = Field(alias='format')

    def __str__(self):

        return f'{self.name} [{self.id}]'

class TableParent(BaseModel):
    id_: str = Field(alias="id")
    type_: str = Field(alias="type")
    href: HttpUrl
    browserLink: HttpUrl
    name: str

class Table(BaseModel):
    id_: str = Field(alias="id")
    type_: constr(regex='table') = Field(alias='type')
    tableType: str
    href: HttpUrl
    browserLink: HttpUrl
    name: str
    parent: TableParent = None # When tableType is 'view', there is no parent, for exmample

    #  def __init__(self,item_dict):
        #  self.columns = self.columns_get()

    def __str__(self):

        return f'{self.name} [{self.id_}]'

    def get_rows(self):

        uri = f"https://coda.io/apis/v1/docs/{settings.CODA_DOC_ID}/tables/{self.id}/rows"
        req = requests.get(uri, headers=config.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        return [Row(item_i, self.columns) for item_i in req.json()['items']]

    def get_columns(self):

        uri = f"https://coda.io/apis/v1/docs/{settings.CODA_DOC_ID}/tables/{self.id_}/columns"
        req = requests.get(uri, headers=settings.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        try:
            return [Column.parse_obj(item_i) for item_i in req.json()['items']]
        except ValidationError as e:
            log.error(f"Error when parsing column json:\n{e.json()}")

class CodaClient(object):

    tables: list = []

    def __init__(self, settings: config.Settings):

        uri = f"https://coda.io/apis/v1/docs/{settings.CODA_DOC_ID}/tables"
        req = requests.get(uri, headers=settings.CODA_HEADERS)
        req.raise_for_status() # Throw if there was an error.

        try:
            self.tables = [Table.parse_obj(item_i) for item_i in req.json()['items']]
        except ValidationError as e:
            log.error(f"Error when parsing table json:\n{e.json()}")

@lru_cache()
def init_coda(settings: config.Settings = Depends(config.get_settings)) -> object:
    log.info("Initialising Coda client...")
    return CodaClient(settings)

settings = config.Settings()
coda = CodaClient(settings)

for table in coda.tables:

    print(table)
    table.get_columns()

    #  if table.name == "Slack Users":

        #  print(table)
        #  for column in table.columns:
            #  print(f"   {column}")

        #  for row in table.rows_get():
            #  print(row)
