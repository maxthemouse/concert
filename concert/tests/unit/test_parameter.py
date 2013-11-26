from concert.quantities import q
from concert.tests import TestCase
from concert.base import (Parameterizable, Parameter,
                          WriteAccessError, ReadAccessError, UnitError,
                          SoftLimitError, HardLimitError)
# from concert.devices.motors.dummy import Motor


class BaseDevice(Parameterizable):

    foo = Parameter(unit=q.m)

    def __init__(self):
        super(BaseDevice, self).__init__()


class FooDevice(BaseDevice):

    def __init__(self, default):
        super(FooDevice, self).__init__()
        self._value = default

    def _get_foo(self):
        return self._value

    def _set_foo(self, value):
        self._value = value


class RestrictedFooDevice(FooDevice):
    def __init__(self, lower, upper):
        super(RestrictedFooDevice, self).__init__(0 * q.mm)
        self['foo'].lower = lower
        self['foo'].upper = upper


class ConvertingDevice(FooDevice):
    def __init__(self):
        super(ConvertingDevice, self).__init__(0 * q.mm)
        self['foo'].conversion = lambda x: x / q.m * q.count


class TestParameterizable(TestCase):

    def setUp(self):
        super(TestParameterizable, self).setUp()
        self.foo1 = FooDevice(42 * q.m)
        self.foo2 = FooDevice(23 * q.m)

    def test_property_identity(self):
        self.foo1.foo = 15 * q.m
        self.assertEqual(self.foo1.foo, 15 * q.m)
        self.assertEqual(self.foo2.foo, 23 * q.m)

    def test_func_identity(self):
        self.foo1.set_foo(15 * q.m).wait()
        self.assertEqual(self.foo1.get_foo().result(), 15 * q.m)
        self.assertEqual(self.foo2.get_foo().result(), 23 * q.m)

    def test_parameter_property(self):
        self.assertEqual(self.foo1['foo'].unit, q.m)

    def test_saving(self):
        m = FooDevice(0 * q.mm)

        m.foo = 1 * q.mm
        m.stash().wait()
        m.foo = 2 * q.mm
        m.stash().wait()
        m.foo = 0.123 * q.mm
        m.foo = 1.234 * q.mm

        m.restore().wait()
        self.assertEqual(m.foo, 2 * q.mm)

        m.restore().wait()
        self.assertEqual(m.foo, 1 * q.mm)

    def test_soft_limit_change(self):
        limited = FooDevice(0 * q.mm)
        limited['foo'].lower = -2 * q.mm
        limited['foo'].upper = 2 * q.mm

        limited.foo = -1.5 * q.mm
        limited.foo = +1.5 * q.mm

        with self.assertRaises(SoftLimitError):
            limited.foo = 2.5 * q.mm

    def test_soft_limit_restriction(self):
        limited = RestrictedFooDevice(-2 * q.mm, 2 * q.mm)
        self.assertEqual(limited['foo'].lower, -2 * q.mm)
        self.assertEqual(limited['foo'].upper, +2 * q.mm)

    def test_conversion(self):
        device = ConvertingDevice()
        device.foo = 2 * q.m
        self.assertEqual(device._value, 2 * q.count)

        device.foo = 0 * q.m
        self.assertEqual(device.foo, 0 * q.m)
