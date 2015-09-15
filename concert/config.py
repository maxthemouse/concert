"""
.. data:: ENABLE_ASYNC

    Enable asynchronous execution. If disabled, dummy futures are used that do
    no execute synchronously.

.. data:: ENABLE_GEVENT

    Turn on gevent support. If geven is not available, fall back to
    ThreadPoolExecutor approach.

.. data:: MOTOR_VELOCITY_SAMPLING_TIME

    Time step for calculation of motor velocity by measuring two postion
    values. Longer values will create more acurate results but reading the
    velocity will take more time.
"""
from concert.quantities import q

ENABLE_ASYNC = True
ENABLE_GEVENT = False

MOTOR_VELOCITY_SAMPLING_TIME = 0.1 * q.s
