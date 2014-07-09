App Wedding
-----------

A simple google appengine based wedding website. Should be easy to fork and 
manipulate to your own needs.

Modify app.yaml so it fits your own deployment

Modify templates/ to fit your needs

Requires 
--------

* Python 2.7
* [google appengine python 2.7 SDK](https://developers.google.com/appengine/downloads)

Examples
--------

**run locally**

    google_appengine/dev_appserver.py app-wedding/

**deployment**

    google_appengine/appcfg.py update app-wedding/
