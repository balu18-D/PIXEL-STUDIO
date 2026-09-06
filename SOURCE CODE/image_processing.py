import cv2
import numpy as np


def process_image(image, operation):
    

    # =====================================================
    # COLOR OPERATIONS
    # =====================================================

    if operation == "Grayscale":

        return cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

    elif operation == "RGB to HSV":

        return cv2.cvtColor(
            image,
            cv2.COLOR_RGB2HSV
        

        )
         

    elif operation == "Hue":

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2HSV
        )

        return hsv[:, :, 0]

    elif operation == "Saturation":

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2HSV
        )

        return hsv[:, :, 1]

    elif operation == "Value":

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2HSV
        )

        return hsv[:, :, 2]

    # =====================================================
    # ENHANCEMENT
    # =====================================================

    elif operation == "Histogram":

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        return cv2.equalizeHist(gray)

    elif operation == "Brightness":

        return cv2.convertScaleAbs(
            image,
            alpha=1.0,
            beta=40
        )

    elif operation == "Contrast":

        return cv2.convertScaleAbs(
            image,
            alpha=1.5,
            beta=0
        )

    # =====================================================
    # FILTERS
    # =====================================================

    elif operation == "Average Blur":

        return cv2.blur(
            image,
            (5, 5)
        )

    elif operation == "Gaussian Blur":

        return cv2.GaussianBlur(
            image,
            (5, 5),
            1
        )

    elif operation == "Canny Edge":

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        return cv2.Canny(
            gray,
            100,
            200
        )

    elif operation == "Sobel Edge":

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        sobel_x = cv2.Sobel(
            gray,
            cv2.CV_64F,
            1,
            0,
            ksize=3
        )

        sobel_y = cv2.Sobel(
            gray,
            cv2.CV_64F,
            0,
            1,
            ksize=3
        )

        magnitude = cv2.magnitude(
            sobel_x.astype(np.float32),
            sobel_y.astype(np.float32)
        )

        return cv2.convertScaleAbs(
            magnitude
        )

    # =====================================================
    # SHARPENING
    # =====================================================

    elif operation == "Laplacian Sharpening":

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F
        )

        result = gray.astype(np.float64) - laplacian

        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)

    # =====================================================
    # BINARY IMAGE
    # =====================================================

    elif operation == "Binary Image":

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        _, binary = cv2.threshold(
            gray,
            127,
            255,
            cv2.THRESH_BINARY
        )

        return binary

    # =====================================================
    # MORPHOLOGICAL OPERATIONS
    #
    # Original -> Grayscale -> Binary -> 5x5 Kernel
    # =====================================================

    elif operation in [
        "Erosion",
        "Dilation",
        "Opening",
        "Closing"
    ]:

        # Step 1: RGB -> Grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        # Step 2: Grayscale -> Binary
        _, binary = cv2.threshold(
            gray,
            127,
            255,
            cv2.THRESH_BINARY
        )

        # Step 3: 5 x 5 kernel
        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        # Step 4: Operation

        if operation == "Erosion":

            return cv2.erode(
                binary,
                kernel,
                iterations=1
            )

        elif operation == "Dilation":

            return cv2.dilate(
                binary,
                kernel,
                iterations=1
            )

        elif operation == "Opening":

            return cv2.morphologyEx(
                binary,
                cv2.MORPH_OPEN,
                kernel
            )

        elif operation == "Closing":

            return cv2.morphologyEx(
                binary,
                cv2.MORPH_CLOSE,
                kernel
            )

    # =====================================================
    # NO OPERATION
    # =====================================================

    return image
