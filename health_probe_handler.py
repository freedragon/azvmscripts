#!/usr/bin/python3

# simple HTTP server which run a simple page for health probe

from bottle import route, run, redirect, response
from logconfig import logger
from configuration import config
from InstanceMetadata import instanceMetadata
import requests, json, os


hostname = '0.0.0.0'
hostport = 9000
instance_status = 200

def writebody():
    body = '<html><head><title>VM Health Check</title></head>'
    body += '<body><h2> ' + hostname + ' is Healthy </h2><ul><h3></body></html>'
    return body

@route('/')
def root():
    return writebody()

@route('/health')
def isHealthy():
    metadata = instanceMetadata().populate()
    logger.info(metadata)

    if instance_status == 200 and metadata.isPendingDelete():
        instance_status = 410 # HTTP Status Code 410 (Gone)

    response.status = instance_status

    return writebody()

run(host=hostname, port=hostport)

