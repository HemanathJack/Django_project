"""IOT Common backend library
"""
import ast
import os, re
from Application.py_files.common_lib.robot_test_case_op import robot_test_case_op

IOT_SIMULATORS = ['SIMU01', 'SIMU06', 'SIMU74', 'SIMU44', 'SIMU144', 'SIMU153', 'SIMU232', 'SIMU358', 'SIMU362', 'SIMU376']

CONFIG = "Application/static/resources/iot/rellab_iot/config/iot_config/"

class iot_common(robot_test_case_op):
    """Operation functions for IOT Test functions
    """
    def __init__(self):
        super().__init__()

    def get_config_dict_from_repo(self):
        """Get simulator configuration dictionary from repository
        
        Returns:
            configuration (dict): DTU configurations for EU and CN.
        """
        configuration = dict()
        for _config_file in os.listdir(CONFIG):
            if 'dtu_qa2' in _config_file:
                config = open(CONFIG+_config_file, 'r+')
                if 'china' in _config_file:
                    configuration['CN'] = self.read_and_get_conf_dict_from_file(config, env='cn')
                else:
                    configuration['EU'] = self.read_and_get_conf_dict_from_file(config, env='gl')
        return configuration

    def read_and_get_conf_dict_from_file(self, file, find_threshold=25, env=None):
        """Read dictionary from the python file

        Args:
            file (TextIOWrapper): Python file to read dictionary from.
            find_threshold (int): Max threshold to find the end of dict
        
        Returns:
            Returns dict from the file.
        """
        _converted_dict = dict()
        for _line_number, line in enumerate(file):
            _converted_dict[_line_number] = line
        config = dict()
        for _line_number, line in _converted_dict.items():
            if 'rellab_dict' in line and line.startswith('    simu'):
                device_identifier = self.filter_line(line, spaces=True)[0]
                config[device_identifier] = '{'
                for threshold in range(1, find_threshold):
                    if _converted_dict[_line_number+threshold].startswith('    simu') or _converted_dict[_line_number+threshold]=='\n':
                        config[device_identifier] = config[device_identifier][:-1]
                        config[device_identifier] = ast.literal_eval(config[device_identifier])
                        break
                    else:
                        _addition_line = self.filter_line(_converted_dict[_line_number+threshold], comments=True).replace('    ', '')
                        # Pattern to match equipement_data info from config as it is a barrier while converting string to dict
                        pattern = r'(lift|esc)_\d+'
                        match = re.search(pattern, _addition_line)
                        if match:
                            _addition_line = _addition_line.replace(match.group(), f'"{match.group()}"')
                        config[device_identifier] = config[device_identifier] + _addition_line
        # TODO: Temporary fix for simu06 need to find why it is missing to convert it into dict and need a refactor.
        for i, j in config.items():
            if i=='simu_06' and env=='gl':
                config[i] = config[i] + '}'
                config[i] = ast.literal_eval(config[i])
        return config

    def simulator_wise_device_identifiers(self):
        """Simulator wise catagorizing device identifiers.

        Returns:
            Dictionary of device identifiers respect to environment and simualtor. (dict)
        """
        returnable = dict()

        for simulator in IOT_SIMULATORS:
            returnable[simulator] = dict()
            for test_env, values in self.get_config_dict_from_repo().items():
                returnable[simulator][test_env] = dict()
                for device_identifiers, configs in values.items():
                    if device_identifiers.split('simu_')[1].startswith(re.findall(r'\d.+', simulator)[0]):
                        returnable[simulator][test_env][device_identifiers] = configs
        return returnable
