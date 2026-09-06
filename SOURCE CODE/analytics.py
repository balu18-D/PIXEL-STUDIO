import base64
import io

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def compute_analytics(image, operation, filename):
    """
    Compute analytics for the ANALYTICS side panel.

    image:
        Original RGB image as NumPy array (uint8).

    operation:
        Currently selected operation name, or "None".

    filename:
        Original uploaded file name.

    Returns:
        Dict of display-ready analytics values.
    """

    height, width = image.shape[:2]

    if len(image.shape) == 3:
        channels = image.shape[2]
    else:
        channels = 1

    gray = to_gray(image)

    avg_brightness = float(np.mean(gray))
    contrast_value = float(np.std(gray))

    estimated_size = image.nbytes / (1024 * 1024)

    status = "Processed" if operation != "None" else "Ready"

    return {
        "file": filename,
        "resolution": f"{width} x {height}",
        "size_mb": f"{estimated_size:.2f} MB",
        "brightness": f"{avg_brightness:.2f}",
        "contrast": f"{contrast_value:.2f}",
        "status": status,
        
        "operation": operation,
    }


def generate_histogram_chart(image):
    """
    Build an RGB channel histogram chart for the ANALYTICS panel,
    styled to match the PIXEL dark theme.

    image:
        RGB image as NumPy array (uint8).

    Returns:
        Base64-encoded PNG string (no data-URI prefix).
    """

    bg_color = "#111323"
    grid_color = "#282c42"
    text_color = "#8589a5"

    fig, ax = plt.subplots(figsize=(4.6, 2.4), dpi=150)

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    colors = {
        "r": "#f5566c",
        "g": "#3ddc84",
        "b": "#4c9bff",
    }

    channel_names = ["r", "g", "b"]

    for i, name in enumerate(channel_names):
        hist = cv2.calcHist(
            [image],
            [i],
            None,
            [256],
            [0, 256],
        )

        ax.plot(
            hist,
            color=colors[name],
            linewidth=1.2,
            alpha=0.9,
        )

    ax.set_xlim([0, 255])
    ax.set_yticks([])
    ax.tick_params(colors=text_color, labelsize=7)

    for spine in ax.spines.values():
        spine.set_color(grid_color)

    ax.grid(color=grid_color, linewidth=0.5, alpha=0.5)

    fig.tight_layout(pad=0.6)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", facecolor=bg_color)
    plt.close(fig)

    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")
