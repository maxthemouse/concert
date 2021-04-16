import numpy as np
from concert.quantities import q
from concert.devices.motors.dummy import ContinuousRotationMotor
from concert.imageprocessing import find_needle_tips
from concert.tests import slow, TestCase
from concert.tests.util.rotationaxis import SimulationCamera
from concert.processes.common import scan, align_rotation_axis
from concert.measures import rotation_axis
from concert.helpers import Region


class TestRotationAxisMeasure(TestCase):

    def setUp(self):
        super(TestRotationAxisMeasure, self).setUp()
        self.x_motor = ContinuousRotationMotor()
        self.y_motor = ContinuousRotationMotor()
        self.z_motor = ContinuousRotationMotor()

        # The bigger the image size, the more images we need to determine
        # the center correctly.
        self.image_source = SimulationCamera(128, self.x_motor["position"],
                                             self.y_motor["position"],
                                             self.z_motor["position"])

        # Allow 1 px misalignment in y-direction.
        self.eps = np.arctan(2 / self.image_source.rotation_radius) * q.rad

    def make_images(self, x_angle, z_angle, intervals=10):
        self.x_motor.position = z_angle
        self.z_motor.position = x_angle
        values = np.linspace(0, 2 * np.pi, intervals) * q.rad
        prange = Region(self.y_motor["position"], values)
        result = [f.result()[1] for f in scan(self.image_source.grab, prange)]

        return result

    def align_check(self, x_angle, z_angle):
        images = self.make_images(x_angle, z_angle)
        tips = find_needle_tips(images)
        phi, psi = rotation_axis(tips)[:2]

        assert phi - x_angle < self.eps
        assert np.abs(psi) - np.abs(z_angle) < self.eps

    def center_check(self, images):
        tips = find_needle_tips(images)
        center = rotation_axis(tips)[2]

        assert np.abs(center[1] - self.image_source.ellipse_center[1]) < 2
        assert np.abs(center[0] - self.image_source.ellipse_center[0]) < 2

    @slow
    def test_out_of_fov(self):
        images = np.random.normal(size=(10, self.image_source.size, self.image_source.size))
        with self.assertRaises(ValueError) as ctx:
            tips = find_needle_tips(images)
            rotation_axis(tips)

        self.assertEqual("No sample tip points found.", str(ctx.exception))

    @slow
    def test_center_no_rotation(self):
        images = self.make_images(0 * q.deg, 0 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_only_x(self):
        self.image_source.scale = (3, 0.33, 3)
        images = self.make_images(17 * q.deg, 0 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_only_z(self):
        images = self.make_images(0 * q.deg, 11 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_positive(self):
        images = self.make_images(17 * q.deg, 11 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_negative_positive(self):
        images = self.make_images(-17 * q.deg, 11 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_positive_negative(self):
        images = self.make_images(17 * q.deg, -11 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_center_negative(self):
        images = self.make_images(-17 * q.deg, -11 * q.deg, intervals=15)
        self.center_check(images)

    @slow
    def test_only_x(self):
        """Only misaligned laterally."""
        self.align_check(0 * q.deg, 0 * q.deg)

    @slow
    def test_only_z(self):
        """Only misaligned in the beam direction."""
        self.align_check(0 * q.deg, 11 * q.deg)

    @slow
    def test_huge_x(self):
        self.image_source.scale = (3, 0.25, 3)
        self.align_check(60 * q.deg, 11 * q.deg)

    @slow
    def test_huge_z(self):
        self.image_source.scale = (3, 0.25, 3)
        self.align_check(11 * q.deg, 60 * q.deg)

    @slow
    def test_positive(self):
        self.align_check(17 * q.deg, 11 * q.deg)

    @slow
    def test_negative_positive(self):
        self.align_check(-17 * q.deg, 11 * q.deg)

    @slow
    def test_positive_negative(self):
        self.align_check(17 * q.deg, -11 * q.deg)

    @slow
    def test_negative(self):
        self.align_check(-17 * q.deg, -11 * q.deg)

    @slow
    def test_pitch_sgn(self):
        self.image_source.size = 512
        # Image acquisition inverts the contrast, so invert it here to get it right there
        self.x_motor.position = 10 * q.deg
        self.y_motor.position = 0 * q.deg
        self.z_motor.position = 0 * q.deg
        eps = 0.1 * q.deg
        align_rotation_axis(self.image_source, self.y_motor, x_motor=self.x_motor,
                            z_motor=self.z_motor, initial_x_coeff=2*q.dimensionless,
                            metric_eps=eps).join()

        assert np.abs(self.x_motor.position) < eps
