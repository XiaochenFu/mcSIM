import unittest
import analysis_tools as tools
from scipy import fft
import numpy as np
import numpy.fft

import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

class TestTools(unittest.TestCase):

    def setUp(self):
        pass

    def test_resample(self):
        """
        Compare resampling in Fourier space vs. real space
        i.e. compare resample() with resample_fourier_sp()
        :return:
        """

        expand_x = 3
        expand_y = 2

        img = np.random.rand(30, 30)
        img_ft = fft.fft2(img)

        img_resampled_rs = tools.resample(img, nx=expand_x, ny=expand_y)
        img_resampled_rs_ft = fft.fft2(img_resampled_rs)

        img_resampled_fs = tools.resample_fourier_sp(img_ft, mx=expand_x, my=expand_y, centered=False)
        img_resampled_fs_rs = fft.ifft2(img_resampled_fs)

        err_fs = np.abs(img_resampled_fs - img_resampled_rs_ft).max()
        err_rs = np.abs(img_resampled_rs - img_resampled_fs_rs).max()

        self.assertTrue(err_fs < 1e-12)
        self.assertTrue(err_rs < 1e-12)

    def test_expand_fourier_sp(self):
        """
        Test expand_fourier_sp() function
        :return:
        """

        arr = np.array([[1, 2], [3, 4]])
        arr_ft = fft.fft2(arr)
        arr_ft_centered = fft.fftshift(arr_ft)

        arr_ft_ex1 = tools.expand_fourier_sp(arr_ft, mx=2, my=2, centered=False)
        arr_ft_ex2 = tools.expand_fourier_sp(arr_ft_centered, mx=2, my=2, centered=True)

        arr_ex1 = fft.ifft2(arr_ft_ex1)
        arr_ex2 = fft.ifft2(fft.ifftshift(arr_ft_ex2))

        self.assertTrue(np.array_equal(arr_ex1, arr_ex2))
        self.assertTrue(np.array_equal(arr_ex1.real, np.array([[1, 1.5, 2, 1.5],
                                                               [2, 2.5, 3, 2.5],
                                                               [3, 3.5, 4, 3.5],
                                                               [2, 2.5, 3, 2.5]])))

    def test_translate_ft(self):
        """
        Test translate_ft() function
        :return:
        """

        img = np.random.rand(100, 100)
        img_ft = fft.fftshift(fft.fft2(fft.ifftshift(img)))
        dx = 0.065

        fx = tools.get_fft_frqs(img.shape[1], dx)
        fy = tools.get_fft_frqs(img.shape[0], dx)
        df = fx[1] - fx[0]

        # x-shifting
        for n in range(1, 20):
            img_ft_shifted = tools.translate_ft(img_ft, [n * df, 0], dx)
            max_err = np.abs(img_ft_shifted[:, :-n] - img_ft[:, n:]).max()
            self.assertTrue(max_err < 1e-7)

        # y-shifting
        for n in range(1, 20):
            img_ft_shifted = tools.translate_ft(img_ft, [0, n * df], dx)
            max_err = np.abs(img_ft_shifted[:-n, :] - img_ft[n:, :]).max()
            self.assertTrue(max_err < 1e-7)

        # x+y shifting
        for n in range(1, 20):
            img_ft_shifted = tools.translate_ft(img_ft, [n * df, n * df], dx)
            max_err = np.abs(img_ft_shifted[:-n, :-n] - img_ft[n:, n:]).max()
            self.assertTrue(max_err < 1e-7)

        # todo: also test approximately gives the right thing for partial pixel shifts (i.e. that the phases make sense)

    def test_fft_frqs(self):

        dt = 0.46436
        for n in [2, 3, 4, 3634, 581]:
            frqs_np = numpy.fft.fftfreq(n, dt)

            # positive and negative frequencies, with f=0 at edge
            frqs_e = tools.get_fft_frqs(n, dt, centered=False, mode="symmetric")
            self.assertAlmostEqual(np.abs(np.max(frqs_e - frqs_np)), 0, places=14)

            # positive and negative frequencies, with f=0 at center
            frqs_c = tools.get_fft_frqs(n, dt, centered=True, mode="symmetric")
            self.assertAlmostEqual(np.abs(np.max(numpy.fft.fftshift(frqs_np) - frqs_c)), 0, places=14)

            # positive frequencies with f=0 at edge
            frqs_e_pos = tools.get_fft_frqs(n, dt, centered=False, mode="positive")
            frqs_np_pos = np.array(frqs_np, copy=True)
            frqs_np_pos[frqs_np_pos < 0] = frqs_np_pos[frqs_np_pos < 0] + 1/dt
            self.assertAlmostEqual(np.abs(np.max(frqs_e_pos - frqs_np_pos)), 0, places=14)

    def test_fft_pos(self):

        dt = 0.46436
        for n in [2, 3, 4, 5, 9, 10, 481, 5468]:
            pos = np.arange(n) * dt

            pos_e = tools.get_fft_pos(n, dt, centered=False, mode="positive")
            self.assertAlmostEqual(np.max(np.abs(pos - pos_e)), 0, places=12)

            pos_c = tools.get_fft_pos(n, dt, centered=True, mode="positive")
            self.assertAlmostEqual(np.max(np.abs(fft.fftshift(pos) - pos_c)), 0, places=12)

            pos = fft.fftshift(pos)
            ind, = np.where(pos == 0)
            pos[:ind[0]] = pos[:ind[0]] - n * dt

            pos_c_symm = tools.get_fft_pos(n, dt, centered=True, mode="symmetric")
            self.assertAlmostEqual(np.max(np.abs(pos - pos_c_symm)), 0, places=12)



if __name__ == "__main__":
    unittest.main()
