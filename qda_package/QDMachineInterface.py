import json
import os
from abc import ABC, abstractmethod
import sys
from datetime import datetime

from .MachineLogAnalytics import start_logging, stop_logging, upload_file_to_s3
from .ApiLogClass import ApiLogClass


class QDMachineInterface(ABC):
    # Mount folder for output files
    __main_folder = "/mnt/qwf-data"

    __data = None
    __error_list = []
    __output_data = {
        'result': '',
        'message': "",
        "error_list": [],
        "data": {},
        "master_args": {}
    }

    # Master args from YAML file
    __master_args = None

    # File read/write variables
    __workflow_name = ""
    __machine_name = ""
    __machinetemplate_name = ""
    __machine_version = ""
    __machine_ID = ""
    __propertyid = 0
    __property_code = ''
    __prog_lang = ""
    __file_folder = ""
    __output_file = ""
    __dependent_machine = ""
    __mode = ""  # live, test, dev

    # Oprational variables
    __input_data = dict()
    __dependent_machine_data = dict()

    __log_folder = None
    machine_logger = None
    __log_file_name = None
    __log_file_path = None

    __mApiLog = None

    def __init__(self):
        try:
            # Read the JSON string from command line argument
            __error_list = self.__read_sys_argument()
            if __error_list and len(__error_list) > 0:
                for e in __error_list:
                    print(e)
                return

            # Create logger object for entire machine log
            self.__log_folder = self.__workflow_name
            os.makedirs(self.__workflow_name, exist_ok=True)
            self.__log_file_name = f'{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().strftime("%H_%M_%S")}_{self.__machine_name}.log'
            self.__log_file_path = os.path.join(self.__workflow_name, self.__log_file_name)
            self.machine_logger = start_logging(self.__log_file_path, self.__machine_name)
            self.machine_logger.info(f'Start Job For Machine ::{self.__machine_name}')

            # Create Workflow folder under main folder
            self.__file_folder = os.path.join(self.__main_folder, self.__workflow_name)
            if not os.path.exists(self.__file_folder):
                self.machine_logger.info(f"Volume path {self.__file_folder} does not exist.")
                os.makedirs(self.__file_folder)
                self.machine_logger.info(f"Volume folder {self.__file_folder} created")
            else:
                self.machine_logger.info(f"Volume path {self.__file_folder} exists.")

            # Update Depandant data
            self.__update_dependent_data()

            # Create API LOG Object
            self.__mApiLog = ApiLogClass(machine_logger=self.machine_logger,
                                         mode=self.__mode,
                                         workflowname=self.__workflow_name,
                                         propertyid=self.__propertyid,
                                         workflowmachinename=self.__machine_name,
                                         machineversion=self.__machine_version,
                                         machinetemplate=self.__machinetemplate_name,
                                         log_file_name=self.__log_file_name)

            # Start workflow
            if self.__mApiLog:
                if self.__machine_name.upper() == "STARTER":
                    self.__mApiLog.workflowlogsave(logdata=f'{self.__workflow_name} started.', status='start')

                # Machine initialized
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call initialized.',
                                                      status='start')

                # Start system details log
                self.__mApiLog.start_system_log()

        except Exception as e:
            err_msg = f"Exception :: {str(e)}"
            print(err_msg)
            self.__error_list.append(err_msg)
        finally:
            pass

    def __set_final_data(self, data):
        """Updates the data."""
        self.__data = data

    def __add_errors(self, errors):
        """Appends new errors to the error list."""
        self.__error_list = errors

    def get_final_data(self):
        return self.__data

    def get_error_list(self):
        return self.__error_list

    def __callback(self, final_data, error_list):
        """
        Callback function passed to the child.
        Used by the child to pass final data and errors to the parent.
        """
        if final_data:
            self.__set_final_data(final_data)
        if error_list:
            self.__add_errors(error_list)

    @abstractmethod
    def receiving(self, input_data, dependent_machine_data, callback):
        pass

    @abstractmethod
    def pre_processing(self, callback):
        pass

    @abstractmethod
    def processing(self, callback):
        pass

    @abstractmethod
    def post_processing(self, callback):
        pass

    @abstractmethod
    def packaging_shipping(self, callback):
        pass

    def start(self):
        """The method that executes the workflow steps."""
        try:
            print("Starting the workflow")

            # Check if initialization encountered any error
            if self.__check_errors(step_name="initialization"):
                self.__write_output_file()
                return

            # Step 1: Receiving, Error Blank, Inform to API
            self.machine_logger.info(f'{self.__machinetemplate_name} call receiving.')
            self.__error_list = []
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call receiving.',
                                                      status='start')
            self.receiving(self.__input_data, self.__dependent_machine_data, self.__callback)
            if self.__check_errors(step_name="receiving"):
                self.__write_output_file()
                return

            # Step 2: Pre-processing
            self.machine_logger.info(f'{self.__machinetemplate_name} call pre_processing.')
            self.__error_list = []
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call pre_processing.',
                                                      status='start')
            self.pre_processing(self.__callback)
            if self.__check_errors(step_name="pre_processing"):
                self.__write_output_file()
                return

            # Step 3: Processing
            self.machine_logger.info(f'{self.__machinetemplate_name} call processing.')
            self.__error_list = []
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call processing.',
                                                      status='start')
            self.processing(self.__callback)
            if self.__check_errors(step_name="processing"):
                self.__write_output_file()
                return

            # Step 4: Post-processing
            self.machine_logger.info(f'{self.__machinetemplate_name} call post_processing.')
            self.__error_list = []
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call post_processing.',
                                                      status='start')
            self.post_processing(self.__callback)
            if self.__check_errors(step_name="post_processing"):
                self.__write_output_file()
                return

            # Step 5: Packaging and Shipping
            self.machine_logger.info(f'{self.__machinetemplate_name} call packaging_shipping.')
            self.__error_list = []
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} call packaging_shipping.',
                                                      status='start')
            self.packaging_shipping(self.__callback)
            if self.__check_errors(step_name="packaging_shipping"):
                self.__write_output_file()
                return

            # Step 2 : Handle output value
            # If no errors are encountered, mark the status as 'success'
            message = "All steps executed successfully!"
            self.machine_logger.info(f'{self.__machinetemplate_name} {message}')
            self.__output_data["result"] = "success"
            self.__output_data["message"] = message
            self.__output_data["error_list"] = self.get_error_list()
            self.__output_data["data"] = self.get_final_data()

            # Step 3 : Write the final output to a file
            self.__write_output_file()

            # Step 4 : Stop Property Level logging file
            stop_logging(self.machine_logger)

            # Step 5 : Upload logger file into S3
            if self.__workflow_name and self.__log_file_path and self.__log_file_name:
                upload_file_to_s3(local_file_path=self.__log_file_path, file_name=self.__log_file_name,
                                  workflow=self.__workflow_name)

        except Exception as e:
            print(f"Workflow stopped due to an error: {str(e)}")
        finally:
            print("Machine execution finished !!!")
            if self.__machine_name.upper() == "EXIT":
                if self.__mApiLog:
                    self.__mApiLog.workflowlogsave(logdata=f'{self.__workflow_name} end.', status='end')

            # Step 6 : Handle System outpput
            if self.__output_data and self.__output_data['result'] == 'success':
                # Machine success
                if self.__mApiLog:
                    self.__mApiLog.workflowmachinelogsave(
                        logdata=f'{self.__machinetemplate_name} successfully finished.',
                        status='end')
                sys.exit(0)  # Zero exit code indicates success
            else:
                # Machine failed
                e_list = self.__error_list
                e_list.insert(0, self.__output_data['message'])
                error_string = "\n".join(e_list)
                print(error_string)
                if self.__mApiLog:
                    self.__mApiLog.workflowmachinelogsave(logdata=f'{self.__machinetemplate_name} {error_string}',
                                                          status='failed')
                sys.exit(1)  # Non-zero exit code indicates failure

    def __check_errors(self, step_name):
        """Helper function to check for errors and stop workflow if errors are found.
            :param step_name: File to upload
            :return: True if not found error
            """
        if self.__error_list and len(self.__error_list) > 0:
            print(f"Error encountered: {self.__error_list}. Stopping workflow.")
            # Update __output_data with failed status if there are errors
            message = f"{step_name} step did not execute."
            self.__output_data["result"] = "failed"
            self.__output_data["message"] = message
            self.__output_data["error_list"] = self.get_error_list()
            self.__output_data["data"] = self.get_final_data()

            e_list = self.__error_list
            e_list.insert(0, self.__output_data['message'])
            error_string = "\n".join(e_list)
            print(error_string)
            if self.__mApiLog:
                self.__mApiLog.workflowmachinelogsave(logdata=f'{step_name} {error_string}',
                                                      status='failed')
            return True
        return False

    def __read_sys_argument(self):
        """Read and parse JSON string from command line arguments.
            :return: True if not found error
            """
        error_list = []
        try:
            if len(sys.argv) < 2:
                print("ERROR =>>>>> command line arguments is empty, please try again!!!")
                return False

            json_str = sys.argv[1]
            self.__master_args = json.loads(json_str)

            if not isinstance(self.__master_args, dict):
                print("ERROR =>>>>> command line arguments' must be a dictionary (JSON object).")
                return False

            if not self.__master_args:  # This checks if the dictionary is empty
                print("ERROR =>>>>> command line arguments is empty, please try again!!!")
                return False

            self.__output_data["master_args"] = self.__master_args

            if 'mode' in self.__master_args:
                self.__mode = self.__master_args['mode']
            else:
                self.__mode = "dev"

            if 'workflow_name' in self.__master_args:
                self.__workflow_name = self.__master_args['workflow_name']
            else:
                self.__workflow_name = "TestWorkFlow"

            if 'machinetemplate_name' in self.__master_args:
                self.__machinetemplate_name = self.__master_args['machinetemplate_name']
            else:
                self.__machinetemplate_name = "TestTemplate"

            if 'machine_ID' in self.__master_args:
                self.__machine_ID = self.__master_args['machine_ID']
            else:
                self.__machine_ID = 0

            if 'machine_version' in self.__master_args:
                self.__machine_version = self.__master_args['machine_version']
            else:
                self.__machine_version = '1.0.0'

            if 'prog_lang' in self.__master_args:
                self.__prog_lang = self.__master_args['prog_lang']
            else:
                self.__prog_lang = 'python'

            if 'machine_name' in self.__master_args:
                self.__machine_name = self.__master_args['machine_name']
            else:
                msg = f"Key 'machine_name' is not available in input data."
                error_list.append(msg)

            if self.__machine_name is None or self.__machine_name == "":
                msg = f"'machine_name' is None or Blank"
                error_list.append(msg)

            if 'input_data' in self.__master_args:
                self.__input_data = self.__master_args['input_data']
            else:
                msg = f"Key 'input_data' is not available in input data."
                error_list.append(msg)

            if not isinstance(self.__input_data, dict):
                msg = f"'input_data' must be a dictionary (JSON object)."
                error_list.append(msg)

            if 'output' in self.__master_args:
                self.__output_file = self.__master_args['output']
            else:
                msg = f"Key 'output' is not available in input data."
                error_list.append(msg)

            if not isinstance(self.__output_file, str):
                msg = f"'output' must be a string."
                error_list.append(msg)

            if not self.__output_file.endswith('.json'):
                msg = f"'output' must end with '.json' extension."
                error_list.append(msg)

            if 'depends_machine' in self.__master_args:
                self.__dependent_machine = self.__master_args['depends_machine']
            else:
                error_list.append("Key 'depends_machine' is not available in input data.")

            if not isinstance(self.__dependent_machine, list):
                msg = f"'depends_machine' must be a list."
                error_list.append(msg)

            # # Get property code and id from input data
            # if self.__input_data:
            #
            #     if 'property_id' in self.__input_data:
            #         self.__propertyid = self.__master_args['property_id']
            #
            #     if 'property_code' in self.__input_data:
            #         self.__property_code = self.__input_data['property_code']

            print(f"input data : {self.__input_data}")
        except json.JSONDecodeError:
            print("ERROR =>>>>> Invalid JSON string provided.")
        except Exception as e:
            msg = f"Exception :: {str(e)}"
            print(msg)
            error_list.append(msg)
        finally:
            return error_list

    def __update_dependent_data(self):
        print(f"dependent_machine list : {self.__dependent_machine}")
        if self.__dependent_machine and len(self.__dependent_machine) > 0:
            for i in self.__dependent_machine:
                file_path = f"{self.__file_folder}/output_{i}.json"
                if os.path.isfile(file_path):
                    self.machine_logger.info(f"File '{file_path}' exists.")
                    with open(file_path) as json_file:
                        output_json = json.load(json_file)
                        if output_json and output_json['result'] == 'success':
                            if output_json['data']:
                                self.__dependent_machine_data = {**self.__dependent_machine_data,
                                                                 **output_json['data']}
                else:
                    self.machine_logger.info(f"File '{file_path}' does not exist.")

    def __write_output_file(self):
        """Writes the __output_data to a JSON file.
            :return: No any return value
            """
        output_file_path = os.path.join(self.__file_folder, f"output_{self.__output_file}")
        try:
            with open(output_file_path, 'w') as outfile:
                json.dump(self.__output_data, outfile, indent=4)
            print(f"Output written to {output_file_path}")
        except IOError as e:
            print(f"Failed to write output to file: {e}")
