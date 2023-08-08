#!/usr/bin/python3
"""IOT Test Environment
"""
from Application.py_files.iot_ta.iot_common import iot_common
from Application.py_files.common_lib.common import common_api
from SSHLibrary import SSHLibrary

DTU_USERNAME = 'root'
DTU_PWD = 'vMKw7lVuFf7oNkIY'

CONNECTION_TIMEOUT = 60

class iot_environment(iot_common):
    """Operation functions for IOT Test Environments 
    """
    def __init__(self):
        super().__init__()
        self.common = common_api()

    def arrange_ips_and_ports_to_connect(self):
        """Get available ips and ports to initiate connection.
        
        Returns:
            list of ip and port to initiate connection to device 0.0.0.0:22. (list)
        """
        returnable = []
        for simu, test_env in self.simulator_wise_device_identifiers().items():
            for device_id in test_env.values():
                if device_id:
                    for configs in device_id.values():
                        returnable.append(configs['ip'])
        return list(dict.fromkeys(returnable))

    def connect_and_fetch_details(self, configuration):
        """Connect to the configuration and fetch required values

        Args:
            configuration (str): Ip and Port number to get connection.
        
        Returns:
            Live status of particular connection. (dict)
        """
        live_status = dict()
        try:
            ssh = SSHLibrary()
            ssh.open_connection(host=configuration.split(':')[0], port=int(configuration.split(':')[1]), prompt='#', timeout=int(CONNECTION_TIMEOUT))
            ssh.login(username=DTU_USERNAME, password=DTU_PWD)
            ken = self.get_lce_equipement_numbers(ssh)
            live_status[ken] = dict()
            status = self.var_status_kone(ssh)
            live_status[ken]['cellular'] = self.get_network_type(ssh)
            live_status[ken]['status'] = {**status, **self.get_dtu_software(ssh)}
            live_status[ken]['status']['device_model'] = self.get_device_model(ssh)
            ssh.close_connection()
        except:
            pass
        return live_status

    def get_device_model(self, connection):
        """Get DTU device board model from command line.

        Args:
            connection : SSH Connection instance

        Returns:
            DTU board model. (str)
        """
        _output = connection.execute_command('cat /var/status/system | grep device_model')
        _out = _output.split('\n')[0].split('=')[1].strip(' ')
        return _out

    def get_dtu_software(self, connection):
        """Get DTU software version.

        Args:
            connection : SSH Connection instance

        Returns:
            DTU software version. (dict)
        """
        data = connection.execute_command('cat /var/status/system | grep firmware')
        data = data.strip('~ #').split('\n')
        for element in data:
            if 'firmware_version_full' not in element:
                return {element.split(' = ')[0] : element.split(' = ')[1].replace('\r', '')}

    def get_ip_and_model_with_loc_for_all_simulators(self):
        """Get ip, model and location of simulator from configuration
        
        Note:
            The reason to get IP from only EU file is that, majority of simupc has EU and
            also considering NA DTUs and other side functional DTUs
        
        Returns:
            Dictionary of simualtors with ip, model and location. (dict)
        """
        _configuration = self.get_config_dict_from_repo()['EU']
        _simulatos = ['SIMU01', 'SIMU06', 'SIMU74', 'SIMU44', 'SIMU144', 'SIMU153', 'SIMU232', 'SIMU358', 'SIMU362', 'SIMU376']

        _returnable = dict()
        for key, value in _configuration.items():
            for simu in _simulatos:
                if simu.lower() in key.replace('_', ''):
                    _ip = value['ip'].split(':')[0]
                    _model = value['cpu']['model']
                    if simu == 'SIMU44':
                        _loc = 'USA'
                    elif simu == 'SIMI06' or simu == 'SIMI01' or simu:
                        _loc = 'FRD'
                    else:
                        _loc = 'ITEC'
                    _returnable[simu] = {
                        'ip' : _ip, 'model': _model, 'location': _loc
                    }
        return _returnable

    def get_lce_equipement_numbers(self, connection):
        """Fetch DTU KEN number from configuration

        Args:
            connection : SSH Connection instance

        Returns:
            DTU registered ken. (str) 
        """
        data = connection.execute_command('cat /var/config/kone | grep lce_equipment_number')
        data = data.strip('~ #').split('\n')
        for element in data:
            if element != '' and 'lce_equipment_number_lift2' not in element:
                return element.split(' = ')[1].replace('\r', '')

    def get_network_type(self, connection):
        """Fetch DTU network type

        Args:
            connection : SSH Connection instance

        Returns:
            DTU network type. (str) 
        """
        data = connection.execute_command('cat /var/status/cellular | grep network_type')
        data = data.replace('\r\n', '').strip('~ #')
        data = data.replace(' ', '')
        return {data.split('=')[0] : data.split('=')[1]}

    def get_status_for_device_identifiers(self):
        """Run all the device identifiers paralley in threading function to get live data.

        Returns:
            Live data of all device identifiers in both environments. (dict)
        """
        unavailable_live_status = {
            'status' : {'firmware_version': 'NA', 'firmware_version_full': 'NA', 'controller_type': 'NA',
                'controller_connection_status': 'NA', 'model': 'NA',
                'software_version': 'NA', 'iot_connection_status': 'NA',
                'device_model': 'NA'},
            'cellular' : {'network_type' : 'NA'}
        }
        ken_results = self.common.parallel_executing_functions(self.connect_and_fetch_details, self.arrange_ips_and_ports_to_connect())
        _results = dict()
        for _dict in ken_results:
            _results = {**_results, **_dict}
        _simulator = self.simulator_wise_device_identifiers()
        returnable = dict()
        for simulator, device_values in _simulator.items():
            returnable[simulator] = dict()
            for test_env, device_identifiers in device_values.items():
                returnable[simulator][test_env] = dict()
                for device_id, configs in device_identifiers.items():
                    if configs['ken'] in _results:
                        returnable[simulator][test_env][device_id] = _results[configs['ken']]
                    else:
                        returnable[simulator][test_env][device_id] = unavailable_live_status
        return returnable

    def var_status_kone(self, connection):
        """DTU status results

        Args:
            connection : SSH Connection instance

        Returns:
            DTU status results in dictionary. (dict) 
        """
        data=connection.execute_command('cat /var/status/kone')
        data_list = data.strip('~ #').split("\n")
        data_dict = dict()
        for element in data_list:
            if '=' in element:
                data_dict[element.split(' = ')[0]] = element.split(' = ')[1].replace('\r', '')
        if 'app_version' in data_dict:
            del data_dict['app_version']
        return data_dict
