from django import template

register = template.Library()

TYPES = {
    '219': 'Serial Number',
    '220': 'Average Battery Voltage (Last 12 Hours)',
    '221': 'Max Battery Voltage (Last 12 Hours)',
    '222': 'Min Battery Voltage (Last 12 Hours)',
    '223': 'Battery Critical State Count',
    '224': '1 Hour Samples Count',
    '225': 'Lock Mode Entry Count',
    '226': 'Factory Mode Entry Count',
    '227': 'GSM Sync Button Count',
    '228': 'Stove On/Off Count',
    '229': 'Energy Consumed per Hour',
    '230': 'Left Stove Cooktime per Hour',
    '231': 'Right Stove Cooktime per Hour',
    '232': 'Others'
}

@register.filter(name='type_name')
def type_name(value):
    return TYPES[str(value)]
