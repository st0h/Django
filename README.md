# The Blue Hydrangea

This project contains the code and assets for my BBS, [The Blue Hydrangea.](https://hydrangea.sytes.net)
It makes use of the great open-source web framework [Django,](https://www.djangoproject.com/) as well as its 
companion server software, [Daphne,](https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/daphne/) to allow 
one to easily create a site where users can post content and interact!

## System Requirements

To run the application, you will first need to install the following software:

- [Python](https://python.org)
- [Django](https://djangoproject.com)
- [Daphne](https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/daphne/)
- [Python-Markdown](https://python-markdown.github.io/)

## Getting Started

**Note:** A file that contains sensitive information, such as encryption keys and database connection settings, 
must be created at **website/website/settings.py** before you proceed. The settings in this file are specific 
to your own installation and web server software, so is not included with this release. Check out 
the [Django](https://djangoproject.com) tutorials to get started on creating your own!

Once ready, run the following commands in a terminal to copy the app's static files to the directory specified:

```
    cd website
    python3 manage.py collectstatic
```

Next, initialize the database:

You will be notified if the database has been initialized successfully. After that, you can create an administrator
account by running the following:

```
    python3 manage.py createsuperuser
```

Finally, launch the application by running the following:

```
    daphne website.asgi:application --port=9000
```

The port number in the above example can be substituted for any available port on your system. It is 
**highly** recommend running the application behind a web server that serves as a "reverse proxy" to
the application itself. [Caddy](https://caddyserver.com) is one good option!

## License

See **LICENSE.md** for details.
