"""
A :class:`Camera` can be set via the device-specific properties that can be set
and read with :meth:`.ConcertObject.set` and :meth:`.ConcertObject.get`.
Moreover, a camera provides means to

* :meth:`Camera.record` frames,
* :meth:`Camera.stop` the acquisition and
* :meth:`Camera.trigger` a frame capture.

To setup and use a camera in a typical environment, you would do::

    from concert.devices.cameras.uca import UcaCamera

    camera = UcaCamera('pco')
    camera.set('exposure-time', 0.2 * q.s)
    camera.record()
    camera.trigger(blocking=True)
    camera.stop()
"""
from concert.base import Device


class Camera(ConcertObject):
    """Base class for remotely controllable cameras."""

    def __init__(self):
        super(Camera, self).__init__()

    def record(self):
        """Start recording frames."""
        self._record_real

    def stop(self):
        """Stop recording frames."""
        self._stop_real

    def trigger(self):
        """Trigger a frame if possible."""
        self._trigger_real

    def _record_real(self):
        raise NotImplementedError

    def _stop_real(self):
        raise NotImplementedError

    def _trigger_real(self):
        raise NotImplementedError
