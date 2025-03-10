document.addEventListener("DOMContentLoaded", function () {
    const urlInput = document.getElementById("url");
    const downloadButton = document.getElementById("download-btn");
    const message = document.getElementById("message");

    // Function to download reel
    function downloadReel() {
        let url = urlInput.value.trim();

        if (!url) {
            message.innerText = "Please enter a valid URL!";
            return;
        }

        downloadButton.innerText = "Downloading...";
        downloadButton.disabled = true;
        message.innerText = "";

        fetch("https://reelxtract.onrender.com/download", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Download failed");
            }
            return response.blob();
        })
        .then(blob => {
            let link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = "Instagram_Reel.mp4";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            downloadButton.innerText = "Downloaded";
            message.innerText = "";

            setTimeout(() => {
                downloadButton.disabled = false;
            }, 2000);
        })
        .catch(error => {
            message.innerText = "Error downloading reel";
            console.error(error);
            downloadButton.innerText = "Download";
            downloadButton.disabled = false;
        });
    }

    // Reset button to "Download" when typing in the input
    urlInput.addEventListener("input", function () {
        downloadButton.innerText = "Download";
    });

    // Attach event listener to the button
    downloadButton.addEventListener("click", downloadReel);
});
