import os
from pyzabbix import ZabbixAPI
from logger import logger

class Zabbix:
  def __init__(self):
    self.zapi = ZabbixAPI(os.getenv('ZABBIX_URL'))
    self.zapi.login(os.getenv('ZABBIX_USER'), os.getenv('ZABBIX_PASSWORD'))

    self.severity = [
      "Not classified",
      "Info",
      "Warning",
      "Average",
      "High",
      "Disaster"
    ]
    logger.info('Zabbix activated')

  def get_triggers(self, triggerid):
    try:
      result = self.zapi.do_request('trigger.get',{
            'triggerids': triggerid,
            'selectHosts': 'extend',
            'selectTags': 'extend',
            'filter': { 'value': 1, 'skipDependent': 'true', 'onlyTrue': 'true', 'status': 0 }
      })
      return result['result']
    except Exception as err:
      logger.error(f'Error getting triggers: {err}')
      return None

  def get_problems(self):
    try:
      problems = self.zapi.do_request('problem.get',{
            'recent': 'false',
            'output': 'extend',
            'sortfield': ['eventid'],
            'selectHosts': 'extend',
            'selectTags': 'extend',
      })
      problem_list = []
    except Exception as err:
      logger.error(f'Error getting problems: {err}')
      return []

    for problem in problems['result']:
      # Get the trigger for each problem.
      trigger = self.get_triggers(problem['objectid'])
      if trigger != []:
        problem_list.append({
            'eventid': problem['eventid'],
            'severity': self.severity[int(problem['severity'])],
            'hostname': trigger[0]['hosts'][0]['host'],
            'message': problem['name'],
            'tags': problem['tags']
        })
    logger.info(f'{len(problem_list)} problem(s) retrieved')
    return problem_list
