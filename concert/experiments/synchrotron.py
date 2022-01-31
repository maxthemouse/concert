"""
Module for synchrotron based imaging experiments.
"""
from concert.quantities import q
from concert.experiments.imaging import Radiography as BaseRadiography,\
    SteppedTomography as BaseSteppedTomography, \
    ContinuousTomography as BaseContinuousTomography,\
    ContinuousSpiralTomography as BaseContinuousSpiralTomography, \
    SteppedSpiralTomography as BaseSteppedSpiralTomography


class SynchrotronMixin:
    """
    Mixin to implement the required function start_sample_exposure and stop_sample_exposure in the
    imaging experiments for the synchrotron by opening and closing a shutter.
    """

    def __init__(self, shutter):
        self._shutter = shutter

    async def start_sample_exposure(self):
        """
        Starts the sample exposure.

        This calls *shutter.open()*.
        """
        if await self._shutter.get_state() != "open":
            await self._shutter.open()

    async def stop_sample_exposure(self):
        """
        Stops the sample exposure.

        This calls *shutter.close()*.
        """
        if await self._shutter.get_state() != "closed":
            await self._shutter.close()


class Radiography(SynchrotronMixin, BaseRadiography):
    """
    Radiography experiment
    """
    def __init__(self, walker, flat_motor, radio_position, flat_position, camera, shutter,
                 num_flats=200, num_darks=200, num_projections=3000, separate_scans=True):
        """
        :param walker: Walker for storing experiment data.
        :type walker: concert.storage.Walker
        :param flat_motor: LinearMotor for moving sample in and out of the beam.
        :type flat_motor: concert.devices.motors.base.LinearMotor
        :param radio_position: Position of *flat_motor* that the sample is positioned in the beam.
        :type radio_position: q.mm
        :param flat_position: Position of *flat_motor* that the sample is positioned out of the
            beam.
        :type flat_position: q.mm
        :param camera: Camera to acquire the images.
        :type camera: concert.devices.cameras.base.Camera
        :param shutter: Stutter
        :type shutter: concert.devices.shutters.base.Shutter
        :param num_flats: Number of images for flatfield correction.
        :type num_flats: int
        :param num_darks: Number of images for dark correction.
        :type num_darks: int
        :param num_projections: Number of projections.
        :type num_projections: int
        """
        SynchrotronMixin.__init__(self, shutter)
        BaseRadiography.__init__(self, walker=walker,
                                 flat_motor=flat_motor,
                                 radio_position=radio_position,
                                 flat_position=flat_position,
                                 camera=camera, num_flats=num_flats,
                                 num_darks=num_darks,
                                 num_projections=num_projections,
                                 separate_scans=separate_scans)


class SteppedTomography(SynchrotronMixin, BaseSteppedTomography):
    """
    Stepped tomography
    """
    def __init__(self, walker, flat_motor, tomography_motor, radio_position, flat_position, camera,
                 shutter, num_flats=200, num_darks=200, num_projections=3000,
                 angular_range=180 * q.deg, start_angle=0 * q.deg, separate_scans=True):
        """
        :param walker: Walker for storing experiment data.
        :type walker: concert.storage.Walker
        :param flat_motor: LinearMotor for moving sample in and out of the beam.
        :type flat_motor: concert.devices.motors.base.LinearMotor
        :param tomography_motor: RotationMotor for tomography scan.
        :type tomography_motor: concert.devices.motors.base.RotationMotor
        :param radio_position: Position of *flat_motor* that the sample is positioned in the beam.
        :type radio_position: q.mm
        :param flat_position: Position of *flat_motor* that the sample is positioned out of the
            beam.
        :type radio_position: q.mm
        :param camera: Camera to acquire the images.
        :type camera: concert.devices.camera.base.Camera
        :param shutter: Stutter
        :type shutter: concert.devices.shutters.base.Shutter
        :param num_flats: Number of images for flatfield correction.
        :type num_flats: int
        :param num_darks: Number of images for dark correction.
        :type num_darks: int
        :param num_projections: Number of projections.
        :type num_projections: int
        :param angular_range: Range for the scan of the *tomography_motor*.
        :type angular_range: q.deg
        :param start_angle: Start position of *tomography_motor* for the first projection.
        :type start_angle: q.deg
        """
        SynchrotronMixin.__init__(self, shutter)
        BaseSteppedTomography.__init__(self, walker=walker,
                                       flat_motor=flat_motor,
                                       tomography_motor=tomography_motor,
                                       radio_position=radio_position,
                                       flat_position=flat_position,
                                       camera=camera,
                                       num_flats=num_flats,
                                       num_darks=num_darks,
                                       num_projections=num_projections,
                                       angular_range=angular_range,
                                       start_angle=start_angle,
                                       separate_scans=separate_scans)


class ContinuousTomography(SynchrotronMixin, BaseContinuousTomography):
    """
    Continuous tomography
    """
    def __init__(self, walker, flat_motor, tomography_motor, radio_position, flat_position, camera,
                 shutter, num_flats=200, num_darks=200, num_projections=3000,
                 angular_range=180 * q.deg, start_angle=0 * q.deg, separate_scans=True):
        """
        :param walker: Walker for storing experiment data.
        :type walker: concert.storage.Walker
        :param flat_motor: LinearMotor for moving sample in and out of the beam.
        :type flat_motor: concert.devices.motors.base.LinearMotor
        :param tomography_motor: ContinuousRotationMotor for tomography scan.
        :type tomography_motor: concert.devices.motors.base.ContinuousRotationMotor
        :param radio_position: Position of *flat_motor* that the sample is positioned in the beam.
        :type radio_position: q.mm
        :param flat_position: Position of *flat_motor* that the sample is positioned out of the
            beam.
        :type flat_position: q.mm
        :param camera: Camera to acquire the images.
        :type camera: concert.devices.camera.base.Camera
        :param shutter: Stutter
        :type shutter: concert.devices.shutters.base.Shutter
        :param num_flats: Number of images for flatfield correction.
        :type num_flats: int
        :param num_darks: Number of images for dark correction.
        :type num_darks: int
        :param num_projections: Number of projections.
        :type num_projections: int
        :param angular_range: Range for the scan of the *tomography_motor*.
        :type angular_range: q.deg
        :param start_angle: Start position of *tomography_motor* for the first projection.
        :type start_angle: q.deg
        """
        SynchrotronMixin.__init__(self, shutter)
        BaseContinuousTomography.__init__(self, walker=walker,
                                          flat_motor=flat_motor,
                                          tomography_motor=tomography_motor,
                                          radio_position=radio_position,
                                          flat_position=flat_position,
                                          camera=camera,
                                          num_flats=num_flats,
                                          num_darks=num_darks,
                                          num_projections=num_projections,
                                          angular_range=angular_range,
                                          start_angle=start_angle,
                                          separate_scans=separate_scans)


class ContinuousSpiralTomography(SynchrotronMixin, BaseContinuousSpiralTomography):
    """
    Continuous spiral tomography
    """
    def __init__(self, walker, flat_motor, tomography_motor, vertical_motor, radio_position,
                 flat_position, camera, shutter, start_position_vertical, sample_height,
                 vertical_shift_per_tomogram, num_flats=200, num_darks=200, num_projections=3000,
                 angular_range=180 * q.deg, start_angle=0 * q.deg, separate_scans=True):
        """
        :param walker: Walker for storing experiment data.
        :type walker: concert.storage.Walker
        :param flat_motor: LinearMotor for moving sample in and out of the beam.
        :type flat_motor: concert.devices.motors.base.LinearMotor
        :param tomography_motor: ContinuousRotationMotor for tomography scan.
        :type tomography_motor: concert.devices.motors.base.ContinuousRotationMotor
        :param vertical_motor: ContinuousLinearMotor to translate the sample along the tomographic
            axis.
        :type vertical_motor: concert.devices.motors.base.ContinuousLinearMotor
        :param radio_position: Position of *flat_motor* that the sample is positioned in the beam.
        :type radio_position: q.mm
        :param flat_position: Position of *flat_motor* that the sample is positioned out of the
            beam.
        :type flat_position: q.mm
        :param camera: Camera to acquire the images.
        :type camera: concert.devices.cameras.base.Camera
        :param shutter: Stutter
        :type shutter: concert.devices.shutters.base.Shutter
        :param start_position_vertical: Start position of *vertical_motor*.
        :type start_position_vertical: q.mm
        :param sample_height: Height of the sample.
        :type sample_height: q.mm
        :param vertical_shift_per_tomogram: Distance *vertical_motor* is translated during one
            *angular_range*.
        :type vertical_shift_per_tomogram: q.mm
        :param num_flats: Number of images for flatfield correction.
        :type num_flats: int
        :param num_darks: Number of images for dark correction.
        :type num_darks: int
        :param num_projections: Number of projections.
        :type num_projections: int
        :param angular_range: Range for the scan of the *tomography_motor*.
        :type angular_range: q.deg
        :param start_angle: Start position of *tomography_motor* for the first projection.
        :type start_angle: q.deg
        """
        SynchrotronMixin.__init__(self, shutter)
        BaseContinuousSpiralTomography.__init__(self,
                                                walker=walker,
                                                flat_motor=flat_motor,
                                                tomography_motor=tomography_motor,
                                                vertical_motor=vertical_motor,
                                                radio_position=radio_position,
                                                flat_position=flat_position,
                                                camera=camera,
                                                start_position_vertical=start_position_vertical,
                                                sample_height=sample_height,
                                                vertical_shift_per_tomogram=vertical_shift_per_tomogram,
                                                num_flats=num_flats,
                                                num_darks=num_darks,
                                                num_projections=num_projections,
                                                angular_range=angular_range,
                                                start_angle=start_angle,
                                                separate_scans=separate_scans)


class SteppedSpiralTomography(SynchrotronMixin, BaseSteppedSpiralTomography):
    """
    Stepped spiral tomography
    """
    def __init__(self, walker, flat_motor, tomography_motor, vertical_motor, radio_position,
                 flat_position, camera, shutter, start_position_vertical, sample_height,
                 vertical_shift_per_tomogram,  num_flats=200, num_darks=200, num_projections=3000,
                 angular_range=180 * q.deg, start_angle=0 * q.deg, separate_scans=True):
        """
        :param walker: Walker for storing experiment data.
        :type walker: concert.storage.Walker
        :param flat_motor: LinearMotor for moving sample in and out of the beam.
        :type flat_motor: concert.devices.motors.base.LinearMotor
        :param tomography_motor: RotationMotor for tomography scan.
        :type tomography_motor: concert.devices.motors.base.RotationMotor
        :param vertical_motor: LinearMotor to translate the sample along the tomographic axis.
        :type vertical_motor: concert.devices.motors.base.LinearMotor
        :param radio_position: Position of *flat_motor* that the sample is positioned in the beam.
        :type radio_position: q.mm
        :param flat_position: Position of *flat_motor* that the sample is positioned out of the
            beam.
        :type flat_position: q.mm
        :param camera: Camera to acquire the images.
        :type camera: concert.devices.cameras.base.Camera
        :param shutter: Stutter
        :type shutter: concert.devices.shutters.base.Shutter
        :param start_position_vertical: Start position of *vertical_motor*.
        :type start_position_vertical: q.mm
        :param sample_height: Height of the sample.
        :type sample_height: q.mm
        :param vertical_shift_per_tomogram: Distance *vertical_motor* is translated during one
            *angular_range*.
        :type vertical_shift_per_tomogram: q.mm
        :param num_flats: Number of images for flatfield correction.
        :type num_flats: int
        :param num_darks: Number of images for dark correction.
        :type num_darks: int
        :param num_projections: Number of projections.
        :type num_projections: int
        :param angular_range: Range for the scan of the *tomography_motor*.
        :type angular_range: q.deg
        :param start_angle: Start position of *tomography_motor* for the first projection.
        :type start_angle: q.deg
        """
        SynchrotronMixin.__init__(self, shutter)
        BaseSteppedSpiralTomography.__init__(self, walker=walker,
                                             flat_motor=flat_motor,
                                             tomography_motor=tomography_motor,
                                             vertical_motor=vertical_motor,
                                             radio_position=radio_position,
                                             flat_position=flat_position,
                                             camera=camera,
                                             start_position_vertical=start_position_vertical,
                                             sample_height=sample_height,
                                             vertical_shift_per_tomogram=vertical_shift_per_tomogram,
                                             num_flats=num_flats,
                                             num_darks=num_darks,
                                             num_projections=num_projections,
                                             angular_range=angular_range,
                                             start_angle=start_angle,
                                             separate_scans=separate_scans)
