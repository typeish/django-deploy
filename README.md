What is it?
===========

Django-deploy was created to help Django developers get their sites up and running *fast*. The two prerequisites to deploying your site with django-deploy are that your project is structured properly (read on for details), and that you have a suitable host (currently: Linode running Ubuntu 10.04).

What *isn't* it?
================

Django-deploy doesn't try to be everything to everyone. It won't help you prevent or solve your scaling or security problems, and it won't even get your entire site running if you've got more than the basic non-Python dependencies. Not all these things are out of the question in the future (well, the scaling part definitely is. And probably the security part too), they just aren't a goal of the project right now. That means that you should know the basics of server administration before trusting your code to the whims of (what are essentially) some specialized deployment scripts.

What was that about being "structured properly"?
================================================

It means a few assumptions are made about how you set your projects up. I plan on making this much (much) more flexible soon, but as it stands you've gotta follow the rules to get the benefits. The assumptions:

- You're using django-staticfiles to handle media. After using it for so long, I'm not sure how people get along without it. (Note: Django 1.3 will have nearly the same exact functionality baked in, which means this dependency is going away.)
- You keep your apps in an apps/ directory within your project root. Things get too messy otherwise.
- You've defined a requirements.txt file in your project root with your project's requirements.
- That's it (but I'll add more as I inevitably realize them).

Pinax users will already be familiar with these conventions. In fact, many projects based on the latest alpha release of Pinax (0.9a1 as of this writing) will be able to deploy with only minor changes.

Great, but I don't use Linode and/or Ubuntu 10.04
=================================================

I chose Linode/Ubuntu because a) that's what I use now and b) as far as defaults go, they seem reasonable to me. I plan on expanding this a lot in the future. For those eager or interested enough, I'm open to both code and ideas.
