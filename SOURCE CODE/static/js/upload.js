const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const browseBtn = document.getElementById("browse-btn");
const captureBtn = document.getElementById("capture-btn");
const errorBox = document.getElementById("upload-error");

const video = document.getElementById("camera-video");
const canvas = document.getElementById("camera-canvas");
const cameraControls = document.getElementById("camera-controls");
const snapBtn = document.getElementById("snap-btn");

let cameraStream = null;

function showError(message) {
    errorBox.textContent = message;
}

function uploadFile(file) {
    showError("");

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) {
                showError(data.error || "Upload failed");
                return;
            }
            window.location.href = data.redirect;
        })
        .catch(() => showError("Network error. Try again."));
}

// Browse files
browseBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        uploadFile(fileInput.files[0]);
    }
});

// Drag and drop
["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
    });
});

dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
        uploadFile(file);
    }
});

// Camera capture
captureBtn.addEventListener("click", async () => {
    showError("");

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        video.style.display = "block";
        cameraControls.style.display = "block";
    } catch (err) {
        showError("Camera access denied or unavailable.");
    }
});

snapBtn.addEventListener("click", () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
        const file = new File([blob], "captured_image.png", { type: "image/png" });

        if (cameraStream) {
            cameraStream.getTracks().forEach((track) => track.stop());
        }
        video.style.display = "none";
        cameraControls.style.display = "none";

        uploadFile(file);
    }, "image/png");
});
