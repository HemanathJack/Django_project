from django.contrib import messages
from django.shortcuts import redirect,render

def iot_user(view_func):
    """
    This is a decorator function that checks if the user is part of the IOT Test Automation team.
    """
    def wrap(request, *args, **kwargs):
        if request.user.team != 'IOT Test Automation':
            return render(request, 'not_authorized.html')
        else:
            return view_func(request, *args, **kwargs)
    return wrap