This is a very early version. Good to play around with, but probably not anything more than that.

================
MSGR - Mesenger
================

MSGR is a simple Django app to interact with social media messengers.
As of now it can only interact with Facebook messenger.


Quick start
-----------

1. Add "msgr" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'msgr',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^msgr/', include('mrgr.urls')),

3. Run `python manage.py migrate` to create the msgr models.


