const connectBtn =
    document.getElementById("connectBtn");

const cameraUrl =
    document.getElementById("cameraUrl");

const videoFeed =
    document.getElementById("videoFeed");

const maskFeed =
    document.getElementById("maskFeed");

const percentage =
    document.getElementById("percentage");

const risk =
    document.getElementById("risk");


// ========================================
// Call Toggles
// ========================================

const twilioCall =
    document.getElementById("twilioCall");

const gsmCall =
    document.getElementById("gsmCall");


// ========================================
// Settings
// ========================================

const settingsBtn =
    document.getElementById("settingsBtn");

const settingsModal =
    document.getElementById("settingsModal");

const closeSettings =
    document.getElementById("closeSettings");

const thresholdSlider =
    document.getElementById("thresholdSlider");

const thresholdValue =
    document.getElementById("thresholdValue");

const areaSlider =
    document.getElementById("areaSlider");

const areaValue =
    document.getElementById("areaValue");

const criticalSlider =
    document.getElementById("criticalSlider");

const criticalValue =
    document.getElementById("criticalValue");


// ========================================
// GSM Settings
// ========================================

const gsmPhone =
    document.getElementById("gsmPhone");

const gsmPort =
    document.getElementById("gsmPort");

const gsmBaudrate =
    document.getElementById("gsmBaudrate");

const saveGsmSettings =
    document.getElementById("saveGsmSettings");


// ========================================
// Settings Editing State
// ========================================

let editingGsmSettings = false;


// ========================================
// Connect Camera
// ========================================

connectBtn.onclick = function () {

    let url =
        cameraUrl.value.trim();

    if (url === "") {

        alert(
            "Please enter ESP32 Stream URL"
        );

        return;
    }

    fetch("/connect", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body:
            "url=" +
            encodeURIComponent(url)

    })

    .then(response =>
        response.json()
    )

    .then(data => {

        if (data.success) {

            videoFeed.src =
                "/video?" +
                new Date().getTime();

            maskFeed.src =
                "/mask?" +
                new Date().getTime();

        }

        else {

            alert(
                "Cannot connect to camera."
            );

        }

    })

    .catch(error => {

        console.log(error);

        alert(
            "Connection error."
        );

    });

};


// ========================================
// Twilio Call
// ========================================

twilioCall.addEventListener(
    "change",
    function () {

        fetch("/set_twilio", {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/x-www-form-urlencoded"

            },

            body:
                "enabled=" +
                this.checked

        });

        if (this.checked) {

            gsmCall.checked = false;

        }

    }
);


// ========================================
// GSM Call
// ========================================

gsmCall.addEventListener(
    "change",
    function () {

        fetch("/set_gsm", {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/x-www-form-urlencoded"

            },

            body:
                "enabled=" +
                this.checked

        });

        if (this.checked) {

            twilioCall.checked = false;

        }

    }
);


// ========================================
// Settings Popup
// ========================================

settingsBtn.onclick = function () {

    settingsModal.style.display =
        "block";

};


closeSettings.onclick = function () {

    settingsModal.style.display =
        "none";

};


window.onclick = function (event) {

    if (
        event.target ==
        settingsModal
    ) {

        settingsModal.style.display =
            "none";

    }

};


// ========================================
// GSM Input Editing
// ========================================

gsmPhone.addEventListener(
    "focus",
    function () {

        editingGsmSettings = true;

    }
);


gsmPort.addEventListener(
    "focus",
    function () {

        editingGsmSettings = true;

    }
);


gsmBaudrate.addEventListener(
    "focus",
    function () {

        editingGsmSettings = true;

    }
);


// ========================================
// GSM Input Blur
// ========================================

gsmPhone.addEventListener(
    "blur",
    function () {

        setTimeout(
            checkGsmEditing,
            300
        );

    }
);


gsmPort.addEventListener(
    "blur",
    function () {

        setTimeout(
            checkGsmEditing,
            300
        );

    }
);


gsmBaudrate.addEventListener(
    "blur",
    function () {

        setTimeout(
            checkGsmEditing,
            300
        );

    }
);


function checkGsmEditing() {

    if (
        document.activeElement !== gsmPhone &&
        document.activeElement !== gsmPort &&
        document.activeElement !== gsmBaudrate
    ) {

        editingGsmSettings = false;

    }

}


// ========================================
// Threshold
// ========================================

thresholdSlider.oninput = function () {

    thresholdValue.innerHTML =
        this.value;

    fetch("/set_threshold", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body:
            "value=" +
            this.value

    });

};


// ========================================
// Contour Area
// ========================================

areaSlider.oninput = function () {

    areaValue.innerHTML =
        this.value;

    fetch("/set_area", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body:
            "value=" +
            this.value

    });

};


// ========================================
// Critical Level
// ========================================

criticalSlider.oninput = function () {

    criticalValue.innerHTML =
        this.value;

    fetch("/set_critical", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body:
            "value=" +
            this.value

    });

};


// ========================================
// Save GSM Settings
// ========================================

saveGsmSettings.onclick =
    function () {

        const phone =
            gsmPhone.value.trim();

        const port =
            gsmPort.value.trim();

        const baudrate =
            gsmBaudrate.value.trim();


        if (phone === "") {

            alert(
                "Please enter GSM phone number."
            );

            return;

        }


        if (port === "") {

            alert(
                "Please enter GSM COM port."
            );

            return;

        }


        if (baudrate === "") {

            alert(
                "Please enter GSM baud rate."
            );

            return;

        }


        fetch("/set_gsm_settings", {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/x-www-form-urlencoded"

            },

            body:

                "phone=" +
                encodeURIComponent(phone) +

                "&port=" +
                encodeURIComponent(port) +

                "&baudrate=" +
                encodeURIComponent(baudrate)

        })

        .then(response =>
            response.json()
        )

        .then(data => {

            if (data.success) {

                // Use values returned by server
                gsmPhone.value =
                    data.phone;

                gsmPort.value =
                    data.port;

                gsmBaudrate.value =
                    data.baudrate;

                editingGsmSettings =
                    false;

                alert(
                    "GSM settings saved successfully."
                );

            }

            else {

                alert(
                    "Failed to save GSM settings."
                );

            }

        })

        .catch(error => {

            console.log(error);

            alert(
                "Failed to save GSM settings."
            );

        });

    };


// ========================================
// Update Status
// ========================================

function updateStatus() {

    fetch("/status")

    .then(response =>
        response.json()
    )

    .then(data => {


        // ==================================
        // Flood Status
        // ==================================

        percentage.innerHTML =
            data.percentage + "%";


        risk.innerHTML =
            data.risk;


        // ==================================
        // Call Status
        // ==================================

        twilioCall.checked =
            data.twilio;

        gsmCall.checked =
            data.gsm;


        // ==================================
        // Detection Settings
        // ==================================

        thresholdSlider.value =
            data.threshold;

        thresholdValue.innerHTML =
            data.threshold;


        areaSlider.value =
            data.area;

        areaValue.innerHTML =
            data.area;


        criticalSlider.value =
            data.critical;

        criticalValue.innerHTML =
            data.critical;


        // ==================================
        // GSM Settings
        // ==================================

        // IMPORTANT:
        // Do NOT overwrite GSM inputs
        // while user is editing them.

        if (!editingGsmSettings) {

            gsmPhone.value =
                data.gsm_phone;

            gsmPort.value =
                data.gsm_port;

            gsmBaudrate.value =
                data.gsm_baudrate;

        }

    })

    .catch(error => {

        console.log(error);

    });

}


// ========================================
// Status Update
// ========================================

setInterval(
    updateStatus,
    500
);


// ========================================
// Initial Status
// ========================================

updateStatus();