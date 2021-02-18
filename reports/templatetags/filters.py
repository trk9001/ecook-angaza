import math
from django import template
from reports.models import UnitNumber

register = template.Library()
total_cost_list = []


@register.filter(name='cost')
def cost(value, unit_number):
    obj = UnitNumber.objects.get(unit_number=unit_number)

    try:
        cost = math.ceil((value * obj.country.cost) * 100) / 100
        total_cost_list.append(cost)
        return cost
    except:
        return 0.00


@register.simple_tag
def total_cost():
    return math.ceil((sum(total_cost_list)) * 100) / 100
