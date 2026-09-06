const moduleButtons = document.querySelectorAll(".module-btn");
const originalImg = document.getElementById("original-image");
const processedImg = document.getElementById("processed-image");
const operationLabel = document.getElementById("operation-label");
const statusBanner = document.getElementById("status-banner");
const actionRow = document.getElementById("action-row");
const spinner = document.getElementById("spinner");
const resetBtn = document.getElementById("reset-btn");
const newImageBtn = document.getElementById("new-image-btn");
const saveBtn = document.getElementById("save-btn");
const saveToast = document.getElementById("save-toast");
const histogramChart = document.getElementById("histogram-chart");


/* =========================================================
   ZOOM
   ========================================================= */

const zoomInBtn = document.getElementById("zoom-in");
const zoomOutBtn = document.getElementById("zoom-out");
const zoomResetBtn = document.getElementById("zoom-reset");
const zoomLevelText = document.getElementById("zoom-level");

let zoomLevel = 1;

function updateZoom() {

    originalImg.style.transform = `scale(${zoomLevel})`;
    processedImg.style.transform = `scale(${zoomLevel})`;

    if (zoomLevelText) {
        zoomLevelText.textContent =
            `${Math.round(zoomLevel * 100)}%`;
    }
}

if (zoomInBtn) {
    zoomInBtn.addEventListener("click", () => {

        zoomLevel = Math.min(zoomLevel + 0.1, 3);

        updateZoom();
    });
}

if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", () => {

        zoomLevel = Math.max(zoomLevel - 0.1, 0.5);

        updateZoom();
    });
}

if (zoomResetBtn) {
    zoomResetBtn.addEventListener("click", () => {

        zoomLevel = 1;

        updateZoom();
    });
}


/* =========================================================
   HISTOGRAM
   ========================================================= */

let histogramData = null;

function drawHistogram(histogram) {

    if (!histogramChart || !histogram) {
        return;
    }

    histogramData = histogram;

    const canvas = histogramChart;
    const ctx = canvas.getContext("2d");

    const width = 240;
    const height = 180;

    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    const red = histogram.red;
    const green = histogram.green;
    const blue = histogram.blue;

    const maxValue = Math.max(
        ...red,
        ...green,
        ...blue
    );

    /* Background */

    ctx.fillStyle = "#111323";
    ctx.fillRect(0, 0, width, height);


    /* Grid */

    ctx.strokeStyle = "#252940";
    ctx.lineWidth = 1;

    for (let i = 0; i <= 4; i++) {

        const y = (height / 4) * i;

        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }


    /* Draw RGB channel */

    function drawChannel(data, color) {

        ctx.beginPath();

        for (let i = 0; i < 256; i++) {

            const x = (i / 255) * width;

            const y =
                height -
                (data[i] / maxValue) * (height - 10);

            if (i === 0) {

                ctx.moveTo(x, y);

            } else {

                ctx.lineTo(x, y);
            }
        }

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();
    }


    /* RGB lines */

    drawChannel(red, "#ff4d6d");
    drawChannel(green, "#35d07f");
    drawChannel(blue, "#4da6ff");
}


/* =========================================================
   HISTOGRAM MOUSE VALUE
   ========================================================= */

if (histogramChart) {

    histogramChart.addEventListener("mousemove", function (event) {

        if (!histogramData) {
            return;
        }

        const rect =
            histogramChart.getBoundingClientRect();

        const x =
            event.clientX - rect.left;

        let intensity = Math.round(
            (x / rect.width) * 255
        );

        intensity =
            Math.max(0, Math.min(255, intensity));


        const redValue =
            histogramData.red[intensity] || 0;

        const greenValue =
            histogramData.green[intensity] || 0;

        const blueValue =
            histogramData.blue[intensity] || 0;


        const tooltip =
            document.getElementById("histogram-tooltip");

        if (!tooltip) {
            return;
        }


        tooltip.innerHTML = `
            <div>Intensity: <b>${intensity}</b></div>
            <div style="color:#ff4d6d;">
                Red: ${redValue}
            </div>
            <div style="color:#35d07f;">
                Green: ${greenValue}
            </div>
            <div style="color:#4da6ff;">
                Blue: ${blueValue}
            </div>
        `;


        tooltip.style.display = "block";

        tooltip.style.left =
            Math.min(
                x + 15,
                rect.width - 120
            ) + "px";
    });


    histogramChart.addEventListener("mouseleave", function () {

        const tooltip =
            document.getElementById("histogram-tooltip");

        if (tooltip) {

            tooltip.style.display = "none";
        }
    });
}


/* =========================================================
   EXISTING LOGIC
   ========================================================= */

function setActiveButton(operation) {

    moduleButtons.forEach((btn) => {

        btn.classList.toggle(
            "active",
            btn.dataset.op === operation
        );
    });
}


function updateAnalytics(analytics, currentOperation) {

    document.getElementById("an-file").textContent =
        analytics.file || "—";

    document.getElementById("an-resolution").textContent =
        analytics.resolution;

    document.getElementById("an-size").textContent =
        analytics.size_mb;

    document.getElementById("an-brightness").textContent =
        analytics.brightness;

    document.getElementById("an-contrast").textContent =
        analytics.contrast;

    document.getElementById("an-status").textContent =
        analytics.status;

    document.getElementById("an-operation").textContent =
    currentOperation === "None" ? "Original" : currentOperation;
    /*
       IMPORTANT:
       Operation is updated separately inside runOperation().
       This prevents analytics.operation = "None"
       from overwriting the clicked operation.
    */
}


/* =========================================================
   RUN OPERATION
   ========================================================= */

function runOperation(operation) {

    spinner.classList.add("visible");

    statusBanner.classList.remove("visible");


    fetch("/process", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            operation: operation
        }),

    })

        .then((res) => res.json())

        .then((data) => {

            spinner.classList.remove("visible");


            if (data.error) {
                return;
            }


            /* Original image */

            originalImg.src =
                "data:image/png;base64," +
                data.original;


            /* Processed image */

            processedImg.src =
                "data:image/png;base64," +
                data.processed;


            /* Top operation label */

            operationLabel.textContent =
                data.operation;


            /* Histogram */

            drawHistogram(data.histogram);


            /* Analytics */

            updateAnalytics(data.analytics, operation);
setActiveButton(operation);

            /* =================================================
               OPERATION BLOCK FIX
               ================================================= */

            const operationBox =
                document.getElementById("an-operation");

            if (operationBox) {

                if (
                    operation === "None" ||
                    data.operation === "Original"
                ) {

                    operationBox.textContent =
                        "Original";

                } else {

                    operationBox.textContent =
                        operation;
                }
            }


            /* Active module button */

            setActiveButton(operation);


            /* =================================================
               STATUS
               ================================================= */

            if (operation !== "None") {

                statusBanner.textContent =
                    operation +
                    " applied successfully";

                statusBanner.classList.add("visible");

                actionRow.style.display = "grid";

            } else {

                actionRow.style.display = "none";
            }

        })

        .catch(() => {

            spinner.classList.remove("visible");
        });
}


/* =========================================================
   MODULE BUTTONS
   ========================================================= */

moduleButtons.forEach((btn) => {

    btn.addEventListener("click", () => {

        runOperation(btn.dataset.op);

    });
});


/* =========================================================
   RESET
   ========================================================= */

resetBtn.addEventListener("click", () => {

    runOperation("None");

});


/* =========================================================
   NEW IMAGE
   ========================================================= */

newImageBtn.addEventListener("click", () => {

    fetch("/new-image", {
        method: "POST"
    })

        .then((res) => res.json())

        .then((data) => {

            window.location.href =
                data.redirect;

        });
});


/* =========================================================
   SAVE
   ========================================================= */

saveBtn.addEventListener("click", () => {

    fetch("/save", {
        method: "POST"
    })

        .then((res) => res.json())

        .then((data) => {

            saveToast.textContent =
                data.message ||
                data.error ||
                "";

        });
});


/* =========================================================
   INITIAL LOAD
   ========================================================= */

runOperation("None");