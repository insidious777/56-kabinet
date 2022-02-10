from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response


def forbidden_for_authenticated(view):

    @wraps(view)
    def user_check(request, *args, **kwargs):

        if request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return view(request, *args, **kwargs)

    return user_check


def redirect_if_authenticated(view):

    @wraps(view)
    def user_check(request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect(reverse('menu:main'))

        return view(request, *args, **kwargs)

    return user_check


def preserve_help_text(func):

    @wraps(func)
    def make_preserve(db_field, *args, **kwargs):
        form_field = db_field.formfield(**kwargs)
        help_text = form_field.help_text  # save original help_text

        form_field = func(db_field, *args, **kwargs)

        if form_field:
            form_field.help_text = help_text  # overwrite help_text that was updated in super call

        return form_field

    return make_preserve
