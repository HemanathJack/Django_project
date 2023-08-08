#!/usr/bin/python3
"""Robot test case reader for IOT Test Automation
"""

import os

# Global variables

class robot_test_case_op:
    """Robot Test case file fetching functions
    """
    def __init__(self):
        self.ExcludedFilenames = ['__init__.robot', 'resources', 'kc3view']

    def filter_line(self, line, removables=False, comments=False, spaces=False):
        """Filter and remove unwanted contents from the line.

        Args:
            line (str): line from the file to filter.
            removables (bool): True to remove items from _removable list. Defaults to False.
            comments (bool): True to remove unwanted comments from line. Defaults to False.
            spaces (bool): True to remove all spaces from line and return as list. Defaults to False.

        Returns:
            filtered line.
        """
        _removable = ['[Tags]', '...', 'Force Tags']
        if removables:
            if any(_content in line for _content in _removable):
                for _item in _removable:
                    line = line.replace(_item, '')
        if comments:
            if '#' in line:
                return line.split('#')[0]
        if spaces:
            line = line.replace('\n', '')
            filtered_items = [x for x in line.split(' ') if x != '']
            return filtered_items
        return line.replace('\n', '')
    
    def get_documentation_of_testcase(self, file, test_case, line_threshold=4, find_threshold=5):
        """Fetch documentation of testcase from the file.

        Args:
            file (TextIOWrapper): list of lines in string from the file.
            testcase (str): Test case name to fetch tags.
            line_threshold (int): Max number of lines to check for tags after [Force Tags]. Defaults to 4.
            find_threshold (int): Max number of lines to find [Tags] after test case title. Defaults to 5.
        
        Returns:
            Documentaion of test case (str).
        """
        _converted_dict = dict()
        _doc = None
        for _line_number, line in enumerate(file):
            _converted_dict[_line_number] = self.filter_line(line)
        for _line_number, line in _converted_dict.items():
            if test_case in line:
                for threshold in range(1,find_threshold):
                    try:
                        if not self.is_testcase_title(_converted_dict[_line_number+threshold]):
                            if '[Documentation]' in _converted_dict[_line_number+threshold]:
                                _doc = _converted_dict[_line_number+threshold].replace('    [Documentation]', '').replace('    ', '')
                                doc_line = _line_number+threshold
                                for extend_search in range(1, line_threshold):
                                    if '...' in range(1, doc_line+extend_search):
                                        _doc = _doc + ' ' + _converted_dict[doc_line+extend_search].replace('    ...', '').replace('    ', '')
                    except:
                        pass
        return _doc

    def get_force_tags_from_file(self, file, line_threshold=4):
        """Get force tag values from the file.

        Args:
            file (TextIOWrapper): list of lines in string from the file.
            line_threshold (int): Max number of lines to check for tags after [Force Tags]. Defaults to 4.
        
        Returns:
            force_tags (list): list of force tags.
        """
        file_dict = dict()
        for index, _line in enumerate(file):
            file_dict[index] = _line
        _force_tags = []
        for _line_number, _line in file_dict.items():
            if 'Force Tags' in _line:
                _force_tags = self.filter_line(_line, removables=True, spaces=True)
                for threshold in range(1, line_threshold):
                    try:
                        if '...' in file_dict[_line_number+threshold]:
                            _force_tags = _force_tags + self.filter_line(file_dict[_line_number+threshold], removables=True, spaces=True)
                    except:
                        # This exception will perform when the test suite with no test tags.
                        pass
        return _force_tags

    def get_owner_of_test_case(self, tags):
        """Fetch owner name from the test case tags.

        Args:
            tags (list): List of available tags for test case inc force tags.

        Returns:
            owner name from the tags (str).
        """
        for _tag in tags:
            if 'owner' in _tag:
                return _tag.split('=')[1].replace('.', ' ').title()
        return 'No Owner'

    def get_test_tags_of_test_case(self, file, testcase, line_threshold=4, find_threshold=5):
        """Get test case tags of given test case

        Args:
            file (TextIOWrapper): List of lines in string from the file.
            testcase (str): Test case name to fetch tags.
            line_threshold (int): Max number of lines to check for tags after [Force Tags]. Defaults to 4.
            find_threshold (int): Max number of lines to find [Tags] after test case title. Defaults to 5.
        
        Returns:
            tags (list): list of test tags available for the test case.
        """
        _dict_converted = dict()
        tags = []
        for index, _line in enumerate(file):
            _dict_converted[index] = _line
        for _line_number, _line in _dict_converted.items():
            if testcase in _line:
                for threshold in range(1, find_threshold):
                    try:
                        if '[Tags]' in _dict_converted[_line_number+threshold]:
                            _tag_line = _line_number+threshold
                            tags = self.filter_line(_dict_converted[_tag_line], removables=True, spaces=True)
                            for extend in range(1, line_threshold):
                                if '...' in _dict_converted[_tag_line+extend]:
                                    tags = tags + self.filter_line(_dict_converted[_tag_line+extend], removables=True, spaces=True)
                    except:
                        pass
        return tags

    def is_testcase_title(self, line):
        """Verify whether the line is test case title or not

        Args:
            line (str): lines from the robot file.
        
        Returns:
            True/False (bool).
        """
        _not_contain = ['Documentation', 'Library', 'Force Tags', 'Suite Setup', 'Test Setup', 'Suite Teardown', 'Test Teardown', 'Test Timeout',
                        'Resource', 'Test Timeout', 'Suite Timeout']
        if not line.startswith(' ') and not line.startswith('***'):
            if not all([line.startswith(_exclude) for _exclude in _not_contain]):
                return True
        return False

    def read_suits_and_return_testcase_with_tags(self, path):
        """Fetch every suite from Repository Path and gives test cases  
        
        Args:
            path (str): Repository path from the project static location.
        """
        filename_testcases = dict()
        for _file in os.listdir(path):
            if all(_file_name != _file for _file_name in self.ExcludedFilenames): 
                robot_file = open(path+_file, 'r+')
                testcases = self.read_test_case_names_from_file(robot_file)
                robot_file.seek(0)      
                force_tags = self.get_force_tags_from_file(robot_file)
                robot_file.seek(0)
                case_with_tags = dict()
                for _case in testcases:
                    robot_file.seek(0)
                    case_with_tags[_case] = self.get_test_tags_of_test_case(robot_file, _case) + force_tags
                filename_testcases[_file] = case_with_tags
        return filename_testcases

    def read_test_case_names_from_file(self, file):
        """Read the file and fetch test case name.

        Args:
            file (list): lines from the file.

        Returns:
            test_cases (list): list of robot test case names from the file.
        """
        testcase_finder = ["    ", "**"]
        test_cases = list()
        for _line in file:
            if (all(_content not in _line for _content in testcase_finder) and (_line != '\n')):
                test_cases.append(self.filter_line(_line))
        return test_cases

