# zabbix-slackbot
> Monitor your zabbix-alerts in Slack

This project weaves Zabbix and Slack together and enables you and your team to
catch Zabbix-alerts directly in chat.

## Installing / Getting started

Your best bet is to run it like a micro-service inside a container. You need to
build the image and deploy it. The only thing you need to consider is declaring
the necessary environment variables. 

### Environment variables

These variables is declared in the docker-compose file, but can easily be 
set in a configmap if you deploy this as a pod in K8s.

To get this up and running on your machine, edit the docker-compose.yml
file and set the environment variables in there. 

### Prerequisites

You will need to create a Slack-app and get a Token.

The app needs to be invited into the Slack-channels where you want the alerts to
show up.

You will need a Zabbix-server and a proper (read-only) account.

Docker to build the image, and some container runtime to run it.

### Zabbix tagging

You may not want all the alerts to show up in your Slack channel, or you may
want some type of alerts in one channel and some other alerts in another.

The way this is done is by using tags in Zabbix. Simply tag your templates,
hosts or items with the name **slack** and the value set to the name of your channel.

Pretty easy, eh?

### Building the image

```shell
docker build -t zabbix-slackbot .
```

### Deploying the image on your machine
```shell
docker-compose -f docker-compose.yml up
```
