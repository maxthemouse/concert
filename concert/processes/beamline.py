"""A synchrotron beam line specific processes."""
import numpy as np
from concert.casync import casync, wait
from concert.quantities import q
from concert.imageprocessing import compute_rotation_axis, flat_correct
from concert.helpers import expects, Numeric
from concert.devices.motors.base import LinearMotor, RotationMotor
from concert.devices.cameras.base import Camera
from concert.devices.shutters.base import Shutter


@casync
@expects(Camera, Shutter)
def acquire_dark(camera, shutter):
    """Use *camera* and *shutter* to acquire a dark field."""
    if shutter.state != 'closed':
        shutter.close().join()

    return _grab_software_trigger(camera)


@casync
@expects(Camera, Shutter, LinearMotor, Numeric(1, q.mm))
def acquire_image_with_beam(camera, shutter, flat_motor, position):
    """Use *camera*, *shutter* and *flat_motor* to move the sample to the *position* and acquire an
    image.
    """
    futures = []
    if shutter.state != 'open':
        futures.append(shutter.open())
    futures.append(flat_motor.set_position(position))
    wait(futures)

    return _grab_software_trigger(camera)


@casync
@expects(Camera, Shutter, LinearMotor, RotationMotor, Numeric(1, q.mm), Numeric(1, q.mm))
def determine_rotation_axis(camera, shutter, flat_motor, rotation_motor, flat_position,
                            radio_position):
    """Determine tomographic rotation axis using *camera*, *shutter*, *rotation_motor* and
    *flat_motor* devices.  *flat_position* is the position for making a flat field, *radio_position*
    is the position with the sample in the field of view.
    """
    dark = acquire_dark(camera, shutter).result().astype(np.float32)
    flat = acquire_image_with_beam(camera, shutter, flat_motor, flat_position).result()
    first = acquire_image_with_beam(camera, shutter, flat_motor, radio_position).result()
    rotation_motor.move(180 * q.deg).join()
    last = acquire_image_with_beam(camera, shutter, flat_motor, radio_position).result()

    # flat correct
    flat_corr_first = flat_correct(first, flat, dark=dark)
    flat_corr_last = flat_correct(last, flat, dark=dark)

    return compute_rotation_axis(flat_corr_first, flat_corr_last)


def _grab_software_trigger(camera):
    """Switch *camera* to software trigger source and take an image. The source is restored afterwards.
    """
    camera['trigger_source'].stash().join()
    camera.trigger_source = camera.trigger_sources.SOFTWARE

    try:
        camera.trigger()
        return camera.grab()
    finally:
        camera['trigger_source'].restore().join()
