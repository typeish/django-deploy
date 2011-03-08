To install django-deploy:

    pip install django-deploy

To use django-deploy, you'll also need to set up the target project
properly. At the moment, django-deploy makes the following assumptions:

 * There's a server somewhere running Ubuntu 10.04 that you have sufficient access to (other OSes not tested right now)
 * You've defined a requirements.txt file in the root of your project with all its Python dependencies
 * You're using django-staticfiles to manage static files (django-staticfiles has been merged into Django 1.3)


What is it?
===========

Django-deploy was created to help Django developers get their sites up
and running *fast*. The two prerequisites to deploying your site with
django-deploy are that your project is structured properly, and that you
have a suitable host (currently: Ubuntu 10.04).

What *isn't* it?
================

Django-deploy doesn't try to be everything to everyone. It won't help
you prevent or solve your scaling or security problems, and it won't
even get your entire site running if you've got more than the basic
non-Python dependencies. Not all these things are out of the question
in the future (well, the scaling part definitely is. And probably the
security part too), they just aren't a goal of the project right now.
That meanthat you should know the basics of server administration
before trusting your code to the whims of (what are essentially) some
specialized deployment scripts.

