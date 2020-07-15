import cv2 as cv
import numpy as np

from .tools import ToolWidget


class ResamplingWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(ResamplingWidget, self).__init__(parent)

        filt_size = 3
        em_radius = 2
        em_stddev = 5
        em_error = 0.01
        max_iter = 20

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY).astype(np.float32)
        minimum, maximum, _, _ = cv.minMaxLoc(gray)
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], np.float32)
        kernel /= ((filt_size + 1) * (filt_size + 1))
        alpha0 = np.ones((2 * em_radius + 1, 2 * em_radius + 1), np.float32)
        alpha0[em_radius, em_radius] = 0
        alpha0 /= alpha0.size - 1
        alpha1 = np.zeros((2 * em_radius + 1, 2 * em_radius + 1), np.float32)
        gray0 = np.ravel(gray[em_radius:-em_radius, em_radius:-em_radius])

        block_rows = gray.shape[0] - 2 * em_radius
        block_cols = gray.shape[1] - 2 * em_radius
        resamp = np.array([])
        for i in range(-em_radius, em_radius + 1):
            for j in range(-em_radius, em_radius + 1):
                if i == 0 and j == 0:
                    continue
                block = gray[i+em_radius:i+em_radius+block_rows, j+em_radius:j+em_radius+block_cols]
                block = np.reshape(block, (block.size, 1))
                resamp = block if resamp.size == 0 else np.hstack((resamp, block))

        i = 0
        sigma = em_stddev
        c1 = 1 / (sigma * np.sqrt(2*np.pi))
        c2 = 2 * sigma ** 2
        p0 = 1 / (maximum - minimum)
        while cv.norm(alpha0, alpha1) > em_error and i < max_iter:
            filt = cv.filter2D(gray, cv.CV_32F, alpha1)
            resid0 = cv.absdiff(gray, filt)
            resid = resid0[em_radius:resid0.shape[0]-em_radius, em_radius:resid0.shape[0]-em_radius]
            resid = cv.pow(cv.filter2D(resid, cv.CV_32F, kernel), 2)
            cond = c1 * (1 / cv.exp(resid / c2))
            post = cond / (cond + p0)

            sigma = np.sqrt(np.sum(post * resid) / np.sum(post)) / 2
            alpha0 = np.copy(alpha1)
            weights = np.reshape(post, (post.size, 1))
            # deriv = np.multiply()
            k = 0
