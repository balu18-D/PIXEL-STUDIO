import base64
import io
import os
import uuid

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from PIL import Image
import numpy as np

from image_processing import process_image
from analytics import compute_analytics, generate_histogram_chart

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
OUTPUT_FOLDER = os.path.join(PROJECT_DIR, "OUTPUT")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}

app = Flask(__name__)
app.secret_key = "pixel-dev-secret-key"
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def image_path_for_session():
    """Path to the original uploaded image stored for this session."""
    image_id = session.get("image_id")

    if not image_id:
        return None

    return os.path.join(UPLOAD_FOLDER, f"{image_id}.png")


def np_to_base64(array):
    """Convert a NumPy image array (RGB or grayscale) to a base64 PNG string."""

    image = Image.fromarray(array)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")


# =============================================================
# SCREEN 1 - WELCOME / UPLOAD
# =============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if file is None or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        image = Image.open(file.stream).convert("RGB")
    except Exception as exc:
        return jsonify({"error": f"Unable to open image: {exc}"}), 400

    image_id = uuid.uuid4().hex

    save_path = os.path.join(UPLOAD_FOLDER, f"{image_id}.png")
    image.save(save_path, format="PNG")

    session["image_id"] = image_id
    session["filename"] = file.filename
    session["operation"] = "None"

    return jsonify({"redirect": url_for("workspace")})


# =============================================================
# SCREEN 2 - WORKSPACE / DASHBOARD
# =============================================================

@app.route("/workspace")
def workspace():
    path = image_path_for_session()

    if not path or not os.path.exists(path):
        return redirect(url_for("index"))

    return render_template(
        "workspace.html",
        filename=session.get("filename", ""),
    )


@app.route("/process", methods=["POST"])
def process():
    path = image_path_for_session()

    if not path or not os.path.exists(path):
        return jsonify({"error": "No image uploaded"}), 400

    data = request.get_json(silent=True) or {}
    operation = data.get("operation", "None")

    session["operation"] = operation

    original = np.array(Image.open(path).convert("RGB"))

    if operation == "None":
        processed = original
    else:
        processed = process_image(original, operation)

    filename = session.get("filename", "")

    analytics = compute_analytics(original, operation, filename)

    # RGB histogram data
    hist_r = np.bincount(
        original[:, :, 0].ravel(),
        minlength=256
    )

    hist_g = np.bincount(
        original[:, :, 1].ravel(),
        minlength=256
    )

    hist_b = np.bincount(
        original[:, :, 2].ravel(),
        minlength=256
    )

    return jsonify({
        "original": np_to_base64(original),
        "processed": np_to_base64(processed),
        "operation": operation if operation != "None" else "Original",
        "analytics": analytics,

        "histogram": {
            "red": hist_r.tolist(),
            "green": hist_g.tolist(),
            "blue": hist_b.tolist()
        }
    })

@app.route("/download")
def download():
    path = image_path_for_session()

    if not path or not os.path.exists(path):
        return redirect(url_for("index"))

    operation = session.get("operation", "None")

    original = np.array(Image.open(path).convert("RGB"))

    if operation == "None":
        processed = original
    else:
        processed = process_image(original, operation)

    result_image = Image.fromarray(processed)

    buffer = io.BytesIO()
    result_image.save(buffer, format="PNG")
    buffer.seek(0)

    download_name = operation.replace(" ", "_").replace("→", "to") + ".png"

    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name=download_name,
    )


@app.route("/save", methods=["POST"])
def save_to_output():
    path = image_path_for_session()

    if not path or not os.path.exists(path):
        return jsonify({"error": "No image uploaded"}), 400

    operation = session.get("operation", "None")

    original = np.array(Image.open(path).convert("RGB"))

    if operation == "None":
        processed = original
    else:
        processed = process_image(original, operation)

    result_image = Image.fromarray(processed)

    filename = operation.replace(" ", "_").replace("→", "to") + ".png"
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    result_image.save(output_path, format="PNG")

    return jsonify({"message": f"Saved successfully: OUTPUT/{filename}"})


@app.route("/new-image", methods=["POST"])
def new_image():
    session.pop("image_id", None)
    session.pop("filename", None)
    session.pop("operation", None)

    return jsonify({"redirect": url_for("index")})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
