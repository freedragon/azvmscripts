#!/usr/bin/python3

from logconfig import logger
from configuration import config
# from vminstance import VMInstance
from InstanceMetadata import InstanceMetadata
from bearer_token import BearerAuth
import requests, json, os

vmInstance = InstanceMetadata().populate()
logger.info(vmInstance)

"""
Check if the vm needs to be deleted (Merged into InstanceMedata.py)
"""
def isInstanceinPendingDelete():
    deleteTag = config.get('imds', 'pending_delete_tag')

    if deleteTag in vmInstance.tags:
        return True
    else:
        return False

"""
    Here is where we need to put all the custom tasks that need to be performed
"""
def  performCustomOperation():
    logger.info("Performing custom operation")

    ## This is where the custom logic will go


"""
This will call the health Probe URL and fail it
"""
def failLoadBalancerProbes():
    logger.info("Failing Health Probes")
    try:
        kill_health_probe = config.get('shell-commands', 'kill_health_probe_process')
         # Delete all cron jobs
        kill_process = os.system(kill_health_probe)

        if kill_process is not 0:
            logger.error("Error killing health probe")
    except:
        logger.error("Error in failing health probe")

"""
This will kill the cron job which collects and submits custom metric to Azure Monitor
"""
def stopCustomMetricFlow():
    logger.info("Stopping the Custom Metrics")
    removeCrontab = config.get('shell-commands', 'remove_all_crontab')

    #removeCrontab = "crontab -r"
    
    logger.info("Deleting all cron jobs")
   
    # Delete all cron jobs
    areCronsRemoved = os.system(removeCrontab)

    if areCronsRemoved is not 0:
        logger.error("Error deleting Cron jobs, health probe will not fail")

"""
Call the VMSS Rest API to Delete the VM 
"""
def deleteVMFromVMSS():
    logger.info("Deleting the VM from VMSS")

    vm_delete_url =  config.get('vmss', 'vm_delete_url')
    formatted_url = vm_delete_url.format(subscriptionId = vmInstance.subscriptionId, \
         resourceGroupName = vmInstance.resourceGroupName,\
              vmScaleSetName = vmInstance.vmScaleSetName, instanceId = vmInstance.vmId)

    logger.info("The Delete URL is - " +  formatted_url)

    requests.delete(formatted_url, data={}, auth=BearerAuth(vmInstance.access_token))

#if(isInstanceinPendingDelete()):
if(vmInsance.isPendingDelete()):
    logger.info("Pending Delete is true ...starting custom clean up logic")
    # Backend removal will be handled from web handler.
    # failLoadBalancerProbes()
    stopCustomMetricFlow()
    performCustomOperation()
    deleteVMFromVMSS()
else: 
    logger.info("Instance not in Pending Delete, nothing to do")
