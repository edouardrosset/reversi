#-*- coding:utf-8 -*-
from django import template

register = template.Library()

@register.filter
def concat(a,b):   
    """
    concatenate integers in filter
    """
    return str(a)+str(b)
