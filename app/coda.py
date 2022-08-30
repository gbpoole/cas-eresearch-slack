import config
import codaio
import logging

log = logging.getLogger(__name__)


settings = config.Settings()
coda = config.CodaClient(settings)

query = '"Name":"Greg"'
for row in coda.get_rows('people', query=query):
    print(row)

data = [
    {'Developer': 'Greg','Project':'OzSTAR','Duration [Days]':'5 days'},
    #  {'Developer': 'Greg','Project':'OzSTAR','Duration [Days]':'3 days'},
    #  {'Developer': 'Lewis','Project':'GWCloud','Duration [Days]':'1 week'},
        ]
coda.put_rows('timesheet',data)
