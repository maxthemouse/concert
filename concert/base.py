# -*- coding: utf-8 -*-
"""
A *device* is a software abstraction for a piece of hardware that can be
controlled.

Each device consists of a set of named :class:`Parameter` instances and
device-specific methods. If you know the parameter name, you can get a reference
to the parameter object by using the index operator::

    pos_parameter = motor['position']

To set and get parameters explicitly , you can use the :meth:`Parameter.get` and
:meth:`Parameter.set` methods::

    pos_parameter.set(1 * q.mm)
    print (pos_parameter.get())

.. note::

    Setting and getting values from a parameter are synchronous operations
    and will block execution until the value is set or returned.

Parameters are tied to devices as properties and can be accessed in a more
convenient way::

    motor.position = 1 * q.mm
    print (motor.position)

Parameter objects are not only used to communicate with a device but also carry
meta data information about the parameter. The most important ones are
:attr:`Parameter.name`, :attr:`Parameter.unit` and :attr:`Parameter.limiter` as
well as the doc string describing the parameter. Moreover, parameters can be
queried for access rights using :meth:`Parameter.is_readable` and
:meth:`Parameter.is_writable`.

To get all parameters of an object, you can iterate over the device itself ::

    for param in motor:
        print("{0} => {1}".format(param.unit, param.name))
"""
import re
import threading
import prettytable
from threading import Event
from logbook import Logger
from concurrent.futures import ThreadPoolExecutor, wait
from concert.events.dispatcher import dispatcher
from concert.ui import get_default_table


executor = ThreadPoolExecutor(max_workers=10)


log = Logger(__name__)


class UnitError(ValueError):
    """Raised when an operation is passed value with an incompatible unit"""
    pass


class LimitError(Exception):
    """Raised when an operation is passed a value that exceeds a limit"""
    pass


class ParameterError(Exception):
    """Raised when a parameter is accessed that does not exists"""
    def __init__(self, parameter):
        msg = "`{0}' is not a parameter".format(parameter)
        super(ParameterError, self).__init__(msg)


class ReadAccessError(Exception):
    """Raised when user tries to change a parameter that cannot be written"""
    def __init__(self, parameter):
        log.warn("Invalid read access on {0}".format(parameter))
        msg = "parameter `{0}' cannot be read".format(parameter)
        super(ReadAccessError, self).__init__(msg)


class WriteAccessError(Exception):
    """Raised when user tries to read a parameter that cannot be read"""
    def __init__(self, parameter):
        log.warn("Invalid write access on {0}".format(parameter))
        msg = "parameter `{0}' cannot be written".format(parameter)
        super(WriteAccessError, self).__init__(msg)


class MultiContext(object):
    """Multi context manager to be used in a Python `with` management.

    For example, to use multiple axes safely in one process, all you have to do
    is ::

        with MultiContext([axis1, axis2]):
            axis1.set_position()
            axis2.set_position()

    Original code by João S. O. Bueno licensed under CC-BY-3.0.
    """

    def __init__(self, *args):
        if (len(args) == 1 and
               (hasattr(args[0], "__len__") or
                hasattr(args[0], "__iter__"))):
            self.objs = list(args[0])
        else:
            self.objs = args

    def __enter__(self):
        return tuple(obj.__enter__() for obj in self.objs)

    def __exit__(self, type_, value, traceback):
        return all([obj.__exit__(type_, value, traceback)
                    for obj in self.objs])


def value_compatible(value, unit):
    """Check if a *value* of a quantity is compatible with *unit* and return
    ``True``."""
    try:
        unit + value
        return True
    except ValueError:
        return False


def parameter_name_valid(name):
    """Check if a parameter *name* is correct and return ``True`` if so."""
    expr = r'^[a-zA-Z]+[a-zA-Z0-9_-]*$'
    return re.match(expr, name) is not None


class Parameter(object):
    """A parameter with a *name* and an optional *unit* and *limiter*."""

    CHANGED = 'changed'

    def __init__(self, name, fget=None, fset=None,
                 unit=None, limiter=None,
                 doc=None, owner_only=False):

        if not parameter_name_valid(name):
            raise ValueError('{0} is not a valid parameter name'.format(name))

        self.name = name
        self.unit = unit
        self.limiter = limiter
        self.owner = None
        self._owner_only = owner_only
        self._fset = fset
        self._fget = fget
        self.__doc__ = doc

    def get(self):
        """Try to read and return the current value.

        If the parameter cannot be read, :class:`ReadAccessError` is raised.
        """
        if not self.is_readable():
            raise ReadAccessError(self.name)

        return self._fget()

    def set(self, value, owner=None):
        """Try to write *value*.

        If the parameter cannot be written, :class:`WriteAccessError` is
        raised. Once the value has been written on the device, all associated
        callbacks are called and a message is placed on the dispatcher bus.
        """
        if self._owner_only and owner != self.owner:
            raise WriteAccessError(self.name)

        if not self.is_writable():
            raise WriteAccessError(self.name)

        if self.unit and not value_compatible(value, self.unit):
            msg = "`{0}' can only receive values of unit {1} but got {2}"
            raise UnitError(msg.format(self.name, self.unit, value))

        if self.limiter and not self.limiter(value):
            msg = "{0} for `{1}' is out of range"
            raise LimitError(msg.format(value, self.name))

        def log_access(what):
            msg = "{0}: {1} {2}='{3}'"
            name = self.owner.__class__.__name__
            log.info(msg.format(name, what, self.name, value))

        log_access('try')
        self._fset(value)
        log_access('set')
        self.notify()

    def notify(self):
        """Notify that the parameter value has changed."""
        dispatcher.send(self, self.CHANGED)

    def is_readable(self):
        """Return `True` if parameter can be read."""
        return self._fget is not None

    def is_writable(self):
        """Return `True` if parameter can be written."""
        return self._fset is not None


class _ProppedParameter(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def __get__(self, instance, owner):
        return self.parameter.get()

    def __set__(self, instance, value):
        self.parameter.set(value)


class Device(object):
    """
    The :class:`Device` provides synchronous access to a real hardware device,
    such as a motor, a pump or a camera.

    A :class:`Device` is iterable and returns its parameters of type
    :class:`Parameter` ::

        for param in device:
            msg = "{0} readable={1}, writable={2}"
            print(msg.format(param.name,
                             param.is_readable(), param.is_writable())

    To access a single name parameter object, you can use the ``[]`` operator::

        param = device['position']
        print param.is_readable()

    Each parameter value is accessible as a property. If a device has a
    position it can be read and written with::

        param.position = 0 * q.mm
        print param.position
    """
    def __init__(self, parameters=None):
        self._params = {}

        if parameters:
            for parameter in parameters:
                parameter.owner = self
                self.add_parameter(parameter)

        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, type, value, traceback):
        self._lock.release()

    def __str__(self):
        table = get_default_table(["Parameter", "Value"])
        table.border = False
        readable = (param for param in self if param.is_readable())

        for param in readable:
            table.add_row([param.name, str(param.get().result())])

        return table.get_string(sortby="Parameter")

    def __iter__(self):
        for param in self._params.values():
            yield param

    def __getitem__(self, param):
        if param not in self._params:
            raise ParameterError(param)

        return self._params[param]

    def add_parameter(self, parameter):
        """Add *parameter* to device and install a property of the same name
        for reading and/or writing it."""
        self._params[parameter.name] = parameter
        parameter.owner = self
        setattr(self.__class__, parameter.name, _ProppedParameter(parameter))

        method_name = parameter.name.replace('-', '_')

        if parameter.is_readable():
            setattr(self.__class__, 'get_%s' % method_name, parameter.get)

        if parameter.is_writable():
            setattr(self.__class__, 'set_%s' % method_name, parameter.set)


class ConcertObject(object):
    """
    Base class handling parameters manipulation. Events are produced
    when a parameter is set. The class provides functionality for
    listening to messages.

    A :class:`ConcertObject` is iterable and returns its parameters of type
    :class:`Parameter` ::

        for param in device:
            msg = "{0} readable={1}, writable={2}"
            print(msg.format(param.name,
                             param.is_readable(), param.is_writable())

    A :class:`ConcertObject` consists of optional getters, setters, limiters
    and units for named parameters. Implementations first call
    :meth:`__init__` and then :meth:`add_parameter` to add or supplement
    a parameter.
    """
    def __init__(self):
        pass

    def _register_message(self, param):
        """Register a message on which one can wait."""
        if not hasattr(self.__class__, "_MESSAGE_TYPES"):
            setattr(self.__class__, "_MESSAGE_TYPES", set([param]))
        else:
            self.__class__._MESSAGE_TYPES.add(param)

    @property
    def message_types(self):
        if not hasattr(self.__class__, "_MESSAGE_TYPES"):
            # In order not to get error if no parameters were set.
            return set([])
        else:
            return self.__class__._MESSAGE_TYPES

    def send(self, message):
        """Send a *message* tied with this object."""
        dispatcher.send(self, message)

    def subscribe(self, message, callback):
        """Subscribe to a *message* from this object.

        *callback* will be called with this object as the first argument.
        """
        dispatcher.subscribe(self, message, callback)

    def unsubscribe(self, message, callback):
        """
        Unsubscribe from a *message*.

        *callback* is a function which is unsubscribed from a particular
        *message* coming from this object.
        """
        dispatcher.unsubscribe(self, message, callback)


class AsyncWrapper(object):
    """Asynchronous wrapper for whole whole classes."""
    def __init__(self, instance):
        """Constructor.

        *instance* is the object being wrapped.

        """
        super.__setattr__(self, "_inst", instance)

    def __getattr__(self, attr):
        orig_attr = self._inst.__getattribute__(attr)
        if callable(orig_attr):
            def _async_wrapper(*args, **kwargs):
                return executor.submit(orig_attr, *args, **kwargs)
            return _async_wrapper
        else:
            return orig_attr

    def __setattr__(self, name, value):
        self._inst.__setattr__(name, value)
