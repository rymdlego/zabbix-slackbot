import os
from time import sleep
from time import time
from slack import WebClient
from logger import logger

class Bot:
  def __init__(self, channels):
    self.swc = WebClient(os.getenv('SLACK_TOKEN'))
    self.channels = {}
    for chan in channels:
      self.channels[chan] = self.get_channel_id(chan)
    logger.info('Bot activated')

    self.initialized_time = time()

    self.processed_messages = []

  def get_channel_id(self, channel):
    try:
      if channel in self.channels:
        logger.info(f"Channel ID {self.channels[channel]} "
                    f"retrieved for channel {channel} from local variable")
        return self.channels[channel]
      conversation_list = self.swc.conversations_list(types='public_channel')
      for chan in conversation_list['channels']:
        if chan['name'] == channel:
          channel_id = chan['id']
          logger.info(f'Channel ID {channel_id} retrieved for channel {channel} from Slack API')
          sleep(1)
          return channel_id
      return None
    except Exception as err:
      logger.error(f'Error while getting channel id: {err}')
      sleep(1)
      return None

  def get_messages(self, chan, oldest='0'):
    try:
      conversation_history = \
        self.swc.conversations_history(channel=self.channels[chan], oldest=oldest)
      logger.info('Messages retrieved')
      sleep(1)
      return conversation_history['messages']
    except Exception as err:
      logger.error(f'Error getting messages: {err}')
      return []

  def get_message_id(self, text, chan):
    try:
      conversation_history = self.swc.conversations_history(channel=self.channels[chan])
      for message in conversation_history['messages']:
        if message['text'] == text:
          logger.info('Message id found')
          return message['ts']
        logger.error('Message id not found')
        sleep(1)
        return False
    except Exception as err:
      logger.error(f'Error getting message id: {err}')
      return None

  def clear_all_messages(self):
    for chan in self.channels:
      for message in self.get_messages(chan):
        try:
          self.swc.chat_delete(channel=self.channels[chan], ts=message['ts'])
          sleep(1)
        except Exception as err:
          logger.error(f'Error clearing messages: {err}')
      logger.info(f'Messages cleared in channel { chan }')

  def get_unprocessed_messages(self, command, chan):
    messages = []
    for message in self.get_messages(chan, str(self.initialized_time)[:-1]):
      if command in message['text']:
        if message['ts'] not in self.processed_messages:
          messages.append({ 'ts': message['ts'], 'text': message['text'] })
          self.processed_messages.append(message['ts'])
    return messages

  def post_message(self, text, chan, attachments=None):
    try:
      self.swc.chat_postMessage(channel=self.channels[chan], text=text, attachments=attachments)
      logger.info(f'Message posted: {text}')
      sleep(1)
      return self.get_message_id(text, chan)
    except Exception as err:
      logger.error(f'Error posting message: {err}')
      return None

  def post_threaded_message(self, text, tstamp, chan):
    try:
      self.swc.chat_postMessage(channel=self.channels[chan], thread_ts=tstamp, text=text)
      logger.info(f'Threaded message posted: {text}')
      sleep(1)
    except Exception as err:
      logger.error(f'Error posting threaded message: {err}')

  def update_message(self, text, chan, tstamp):
    try:
      self.swc.chat_update(channel=self.channels[chan], text=text, ts=tstamp)
      logger.info(f'Message updated: {text} {tstamp}')
      sleep(1)
    except Exception as err:
      logger.error(f'Error updating message: {err}')

  def destroy_message(self, chan, tstamp):
    try:
      self.swc.chat_delete(channel=self.channels[chan], ts=tstamp)
      logger.info(f'Message destroyed: {tstamp}')
      sleep(1)
    except Exception as err:
      logger.error(f'Error while destroying message: {err}')

  def add_reaction(self, reaction, chan, tstamp):
    try:
      self.swc.reactions_add(channel=self.channels[chan], timestamp=tstamp, name=reaction)
      logger.info(f'Reaction added: {reaction} {tstamp}')
      sleep(1)
    except Exception as err:
      logger.error(f'Error adding reaction: {err}')
