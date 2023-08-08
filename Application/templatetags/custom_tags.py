#!/usr/bin/python3
"""Custom tag handler for django html template.
"""
from django import template
from django.forms.models import model_to_dict

register = template.Library()


@register.filter(name='addvalue')
def addvalue(field, value):
    """Add custom entry to the html attributes field 'value'

    Args:
        field : field.
        value (str): String to be placed in html attribute 'value'.
    """
    return field.as_widget(attrs={'value': value})


@register.filter(name='addselected')
def addselected(field, value):
    """Add custom entry to the html attributes field 'selected'

    Args:
        field : field.
        value (str): String to be placed in html attribute 'selected'.
    """
    return field.as_widget(attrs={'selected': value})

@register.filter(name='cutall')
def cutall(value):
    """remove all empty spaces in a string

    Args:
        value (str): Value to be cut.

    Returns:
        String without empty spaces. (str)
    """
    return str(value).replace(' ', '')

@register.filter(name='getmodel')
def getmodel(dict, simu):
    """Get cpu model of simulator from the configuration dictionary.
    Args:
        dict (dict): Configuration dict of IP, Model and Location.
        simu (str): Simulator to fetch model from config.
    
    Return:
        Model of the simulator (str)
    """
    return dict[simu]['model']

@register.filter
def keyvalue(dict, key):
    """Parsing variable as key from html to get the value from the dictionary.

    Args:
        dict (dict): Dictionary to fetch data.
        key (str): Key to find the value from the dict.

    Returns:
        Value from the dict (str)
    """
    try:
        return dict[key]
    except KeyError:
        return ''


@register.filter(name='current_percent')
def percent(value):
    """Percentage conversion of the value.

    Args:
        value (str): Value to be converted into percentage.

    Returns:
        Percentage of the value (float).
    """
    try:
        total = (int(value) / 4) * 100
        return total
    except:
        return 0


@register.filter(name='simuwise_not_ready')
def simuwise_not_ready(dictionary, simu):
    """Fetch the correct simulator test cases details which is in not ready state.

    Args:
        dictionary (dict): Dictionary of not_ready and bug_open cases for all simmulators.
        simu (str): simulator details to fetch.

    Returns:
        list of cases (list).
    """
    if simu in dictionary:
        return dictionary[simu]['not_ready']
    return []


@register.filter(name='simuwise_bug_open')
def simuwise_bug_open(dictionary, simu):
    """Fetch the correct simulator test cases details which is in bug open state.

    Args:
        dictionary (dict): Dictionary of not_ready and bug_open cases for all simmulators.
        simu (str): simulator details to fetch.

    Returns:
        list of cases (list).
    """
    if simu in dictionary:
        return dictionary[simu]['bug_open']
    return []

@register.filter(name='split1stelement')
def split1stelement(value, splitwith):
    """Splits the string with specific element and returns the first value from list.

    Args:
        value (str): String to split.
        splitwith (str): String to split with.

    Returns:
        First value from splitted list. (str)
    """
    return value.split(splitwith)[0]


@register.filter(name='target_percent')
def target_value_percentage(value, current):
    """Target percentage width calculation for competency bar chart

    Args:
        value (str): Target value of product.
        current (str): current value of proudct.

    Returns:
        Difference in percentage (float)
    """
    try:
        value = int(value)
    except:
        value = 0
    try:
        current = int(current)
    except:
        current = 0
    if int(value) > int(current):
        _difference = percent(value) - percent(current)
        if _difference < 0:
            return 0
        return _difference
    return 0


@register.filter(name='refine_products')
def refine_p(object_dict):
    """Removing unnecessary spaces in products list to the html

    Args:
        object_dict : product list

    Returns:
        product list with removed unnecessary space (list)
    """
    products = list()
    for i in object_dict:
        products.append(model_to_dict(i)['product_name'])
    products_list = list(products)
    name_refined = list()
    for element in products_list:
        name_refined.append(str(element).replace(" ", ''))
    return name_refined


@register.filter(name='refine_modules')
def refine_m(object_dict):
    """Removing unnecessary spaces in modules list to the html

    Args:
        object_dict : module list

    Returns:
        modules list with removed unnecessary space (list)
    """
    modules = list()
    for i in object_dict:
        modules.append(model_to_dict(i)['module_name'])
    products_list = list(modules)
    name_refined = list()
    for element in products_list:
        name_refined.append(str(element).replace(" ", ''))
    return name_refined
