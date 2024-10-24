import requests
from .SystemInfo import log_system_info
import threading
import time
from .MyConfig import get_log_api_host


class ApiLogClass:
    __machine_logger = None
    __workflowname = None
    __mode = None
    __propertyid = ""
    __workflowmachinename = None
    __machinetemplate = None
    __machineversion = None
    __log_file_name = None

    __log_api_host = ""

    def __init__(self,
                 machine_logger,
                 mode,
                 workflowname,
                 propertyid,
                 workflowmachinename,
                 machinetemplate,
                 machineversion,
                 log_file_name
                 ):
        self.__machine_logger = machine_logger
        self.__workflowname = workflowname
        self.__mode = mode
        self.__propertyid = propertyid
        self.__workflowmachinename = workflowmachinename
        self.__machinetemplate = machinetemplate
        self.__machineversion = machineversion
        self.__log_file_name = log_file_name

        if self.__mode == 'live':
            self.__log_api_host = get_log_api_host()
        elif self.__mode == 'dev':
            self.__log_api_host = get_log_api_host()
        elif self.__mode == 'test':
            self.__log_api_host = get_log_api_host()

    def workflowlogsave(self, logdata, status):
        try:
            # Define the API endpoint
            url = f"{self.__log_api_host}/api/v1/WorkFlow/workflowlogsave"

            # Define the payload (the data you're sending in the POST request)
            form_data = {
                "workflowname": self.__workflowname,
                "logdata": logdata,
                "status": status,
                "propertyid": self.__propertyid,
                "mode": self.__mode
            }

            # Make the POST request
            response = requests.post(url, data=form_data)
        except Exception as e:
            self.__machine_logger.info(f"API LOG:: Workflow Level > {logdata} > {str(e)}")
        finally:
            pass

    def workflowmachinelogsave(self, logdata, status):
        try:
            # Define the API endpoint
            url = f"{self.__log_api_host}/api/v1/WorkFlow/workflowmachinelogsave"

            # Define the payload (the data you're sending in the POST request)
            form_data = {
                "machinetemplate": self.__machinetemplate,
                "workflowname": self.__workflowname,
                "logdata": logdata,
                "status": status,
                "propertyid": self.__propertyid,
                "workflowmachinename": self.__workflowmachinename,
                "log_file_name": self.__log_file_name,
                "mode": self.__mode
            }

            # Make the POST request
            response = requests.post(url, data=form_data)
        except Exception as e:
            self.__machine_logger.info(f"API LOG:: Machine Level Error > {logdata} > {str(e)}")
        finally:
            pass

    def machineusagesave(self, system_log):
        try:

            cpucountlogical = system_log['cpu_information']['cpu_count_logical']
            cpucountphysical = system_log['cpu_information']['cpu_count_physical']
            cpufrequency = system_log['cpu_information']['cpu_frequency']
            cpuusage = system_log['cpu_information']['cpu_usage']
            totalmemorygb = system_log['memory_information']['total_memory_gb']
            availablememorygb = system_log['memory_information']['available_memory_gb']
            memoryusageper = system_log['memory_information']['memory_usage_percentage']
            networkbytessentmb = system_log['network_information']['bytes_sent_mb']
            networkbytesreceivedmb = system_log['network_information']['bytes_received_mb']

            # Define the API endpoint
            url = f"{self.__log_api_host}/api/MachineUsage/save"

            # Define the payload (the data you're sending in the POST request)
            form_data = {
                "workflowname": self.__workflowname,
                "machinetemplate": self.__machinetemplate,
                "machineversion": self.__machineversion,
                "cpucountlogical": cpucountlogical,
                "cpucountphysical": cpucountphysical,
                "cpufrequency": cpufrequency,
                "cpuusage": cpuusage,
                "totalmemorygb": totalmemorygb,
                "availablememorygb": availablememorygb,
                "memoryusageper": memoryusageper,
                "networkbytessentmb": networkbytessentmb,
                "networkbytesreceivedmb": networkbytesreceivedmb,
                "workflowmachinename": self.__workflowmachinename,
                "mode": self.__mode
            }

            # Make the POST request
            response = requests.post(url, data=form_data)
        except Exception as e:
            self.__machine_logger.info(
                f"API LOG:: Machine Level Usage Error > {self.__workflowmachinename} > {str(e)}")
        finally:
            pass

    def start_system_log(self):
        # First Time log
        system_data = log_system_info()
        self.machineusagesave(system_log=system_data)

        # Create a thread to run the method in the background every 5 second
        background_thread = threading.Thread(target=self.__upload_system_log)
        background_thread.daemon = True  # Ensures thread stops when the main program exits
        background_thread.start()

    def __upload_system_log(self):
        # Run in background
        while True:
            system_data = log_system_info()
            self.machineusagesave(system_log=system_data)
            time.sleep(5)
