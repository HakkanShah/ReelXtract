document.addEventListener("DOMContentLoaded", function () {
    const downloadButton = document.getElementById("download-btn");
    const inputField = document.getElementById("url");
    const message = document.getElementById("message");

    downloadButton.addEventListener("click", async function () {
        let url = inputField.value.trim();
        if (!url) {
            message.innerText = "⚠️ Please enter a valid Instagram Reel URL!";
            return;
        }

        downloadButton.innerText = "Downloading...";
        downloadButton.disabled = true; // Disable button during request
        message.innerText = "";

        try {
            let response = await fetch("https://reelxtract.onrender.com/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });

            let data = await response.blob();
            if (!response.ok) {
                throw new Error(await response.text());
            }

            // Create a download link
            let link = document.createElement("a");
            link.href = window.URL.createObjectURL(data);
            link.download = "Instagram_Reel.mp4";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            message.innerText = "✅ Download Complete!";
        } catch (error) {
            message.innerText = `❌ Error: ${error.message}`;
            console.error("Download Error:", error);
        } finally {
            // Restore button state
            downloadButton.innerText = "Download";
            downloadButton.disabled = false;
        }
    });

    // Reset button text when user edits input field
    inputField.addEventListener("input", function () {
        downloadButton.innerText = "Download";
    });
});
