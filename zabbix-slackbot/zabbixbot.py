#!/usr/bin/python
from time import sleep
from time import time
import os
from bot import Bot
from zabbix import Zabbix
from logger import logger

def is_max_age(item):
  if time() - item['timestamp'] > int(os.getenv('MAX_AGE_MINUTES')) * 60:
    return True
  return False

def is_new(item):
  if item['count'] < 1:
    return True
  return False

class Queue:
  def __init__(self):
    self.queue = []
    logger.info('Queue activated')

  def add(self, problem, slack_channel):

    # Replace special characters with html entities.
    problem['message'] = problem['message'].replace('&', '&amp;')
    problem['message'] = problem['message'].replace('<', '&lt;')
    problem['message'] = problem['message'].replace('>', '&gt;')

    self.queue.append({
            'slack_id': '',
            'slack_channel': slack_channel,
            'refreshed': False,
            'destroy': False,
            'resolved': False,
            'count': 0,
            'timestamp': time(),
            'problem': problem
    })
    logger.info('Item added to queue')

  def remove(self, item):
    self.queue.remove(item)
    logger.info('Item removed from queue')

  def is_empty(self):
    if len(self.queue) < 1:
      return True
    return False

  def update(self, problem, slack_channel):

    if self.is_empty():
      self.add(problem, slack_channel)
      return

    # if problem already exists in queue, flag it as refreshed.
    for item in self.queue:
      if problem['eventid'] == item['problem']['eventid']:
        if slack_channel == item['slack_channel']:
          item['refreshed'] = True
          return

    # If no refresh takes place, assume new item and add it to queue.
    self.add(problem, slack_channel)
    return

  def pre_process(self):
    # Run before every cycle. Unrefresh everything in queue.
    logger.info('New cycle started')
    for item in self.queue:
      item['refreshed'] = False
      item['count'] += 1

  def post_process(self):
    # Run after every cycle.
    # Set to resolved or destroy.
    for item in self.queue:
      # Problem has been resolved.
      if not item['refreshed'] and not item['resolved'] and not is_new(item):
        item['resolved'] = True
        item['timestamp'] = time()
        item['count'] = 0
        logger.info(f"Item {item['problem']['eventid']} is marked as resolved")
      # Problem is resolved and should be deleted.
      elif item['resolved'] and time() - item['timestamp'] > int(os.getenv('RESOLVE_MINUTES')) * 60:
        item['destroy'] = True
        logger.info(f"Item {item['problem']['eventid']} has been resolved for "
                    f"{os.getenv('RESOLVE_MINUTES')} minutes and is marked for destruction")
      # Problem reached maximum age and is deleted.
      elif is_max_age(item):
        item['destroy'] = True
        logger.info(f"Item {item['problem']['eventid']} "
                    f"reached maximum age and is marked for destruction")

  def show_queue(self):
    for item in self.queue:
      logger.info(item)


def main():

  channels = os.getenv('SLACK_CHANNEL').split(',')

  # Instantiate the objects
  queue = Queue()
  zabbix = Zabbix()
  slackbot = Bot(channels)

  slackbot.clear_all_messages()

  # Main loop
  while True:

    queue.pre_process()

    # Fetch list of problems and process them in queue.
    problems = zabbix.get_problems()
    for problem in problems:
      for tag in problem['tags']:
        if tag['tag'] == "slack":
          if tag['value'] in slackbot.channels:
            queue.update(problem, tag['value'])

    queue.post_process()

    # Do things in Slack
    for item in queue.queue:
      # Post new items.
      if not item['refreshed'] and not item['resolved']:
        # Set slack icon depending on severity level.
        if item['problem']['severity'] == "Info" or item['problem']['severity'] == "Not classified":
          slack_icon = "large_blue_circle"
        else:
          slack_icon = "red_circle"
        message = (f":{slack_icon}: *{item['problem']['hostname']}*: {item['problem']['message']} "
                   f"_[{item['problem']['severity'].upper()}]_")
        item['slack_id'] = slackbot.post_message(message, item['slack_channel'])
      # Mark as resolved.
      elif item['resolved'] and item['count'] < 1:
        slack_icon = "green_circle"
        message = (f":{slack_icon}: *{item['problem']['hostname']}*: {item['problem']['message']} "
                   f"_[RESOLVED]_")
        slackbot.update_message(message, item['slack_channel'], item['slack_id'])
      # Destroy items.
      elif item['destroy']:
        slackbot.destroy_message(item['slack_channel'], item['slack_id'])
        queue.remove(item)

    sleep(int(os.getenv('ZABBIX_CYCLE_TIME_SECONDS')))

if __name__ == '__main__':
  main()
