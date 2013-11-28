==================
Command line shell
==================

Concert comes with a command line interface that is launched by typing
``concert`` into a shell. Several subcommands define the action of the tool.


Session commands
================

The ``concert`` tool is run from the command line.  Without any arguments, its
help is shown::

    $ concert
    usage: concert [-h] [--version]  ...

    optional arguments:
      -h, --help  show this help message and exit
      --version   show program's version number and exit

    Concert commands:

        start     Start a session
        init      Create a new session
        mv        Move session *source* to *target*
        log       Show session logs
        show      Show available sessions or details of a given *session*
        edit      Edit a session
        rm        Remove one or more sessions
        fetch     Import an existing *session*

The tool is command-driven, that means you call it with a command as its first
argument. To read command-specific help, use::

    $ concert [command] -h

.. note::

    When Concert is installed system-wide, a bash completion for the
    ``concert`` tool is installed too. This means, that commands and options
    will be completed when pressing the :kbd:`Tab` key.

.. _init-command:

init
----

.. program:: concert init

Create a new session with the given name::

    concert init experiment

If such a session already exists, Concert will warn you.

    .. option:: --force

        Create the session even if one already exists with this name.

    .. option:: --imports

        List of module names that are added to the import list.

.. note::

    The location of the session files depends on the chosen installation method.
    If you installed into a virtual environment ``venv``, the files will be
    stored in ``/path/to/venv/share/concert``. If you have installed Concert
    system-wide our without using a virtual environment, it is installed into
    ``$XDG_DATA_HOME/concert`` or ``$HOME/.local/share/concert`` if the former
    is not set. See the `XDG Base Directory Specification
    <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_
    for further information. It is probably a *very* good idea to put the
    session directory under version control.


.. _edit-command:

edit
----

.. program:: concert edit

Edit the session file by launching ``$EDITOR`` with the associated Python
module file::

    concert edit session-name

This file can contain any kind of Python code, but you will most likely just add
device definitions and import processes that you want to use in a session.


log
---

.. program:: concert log

Show log of session::

    concert log session-name

If a session is not given, the log command shows entries from all sessions. By
default, logs are gathered in ``$XDG_DATA_HOME/concert/concert.log``. To change
this, you can pass the ``--logto`` and ``--logfile`` options to the ``start``
command. For example, if you want to output log to ``stderr`` use ::

    concert --logto=stderr start experiment

or if you want to get rid of any log data use ::

    concert --logto=file --logfile=/dev/null start experiment


show
----

.. program:: concert show

Show all available sessions or details of a given session::

    concert show [session-name]


mv
--

.. program:: concert mv

Rename a session::

    concert mv old-session new-session


rm
--

.. program:: concert rm

Remove one or more sessions::

    concert rm session-1 session-2

.. warning::

    Be careful. The session file is unlinked from the file system and no
    backup is made.


.. _fetch-command:

fetch
-----

.. program:: concert fetch

Import an existing session from a Python file::

    concert fetch some-session.py

Concert will warn you if you try to import a session with a name that already
exists.

    .. option:: --force

        Overwrite session if it already exists.

    .. option:: --repo

        The URL denotes a Git repository from which the sessions are imported.

.. warning::

    The server certificates are *not* verified when specifying an HTTPS
    connection!


.. _start-command:

start
-----

.. program:: concert start

Load the session file and launch an IPython shell::

    concert start session-name

The quantities package is already loaded and named ``q``.

    .. option:: --logto={stderr, file}

        Specify a method for logging events. If this flag is not specified,
        ``file`` is used and assumed to be
        ``$XDG_DATA_HOME/concert/concert.log``.

    .. option:: --logfile=<filename>

        Specify a log file if ``--logto`` is set to ``file``.

    .. option:: --loglevel={debug, info, warning, error, critical}

        Specify lowest log level that is logged.

    .. cmdoption:: --non-interactive

        Run the session as a script and do not launch a shell.


Extensions
==========

Spyder
------

.. program:: concert spyder

If Spyder is installed, start the session within the Spyder GUI.