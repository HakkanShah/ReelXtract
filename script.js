document.addEventListener("DOMContentLoaded", function () {
    const downloadButton = document.getElementById("download-btn");
    const inputField = document.getElementById("url");
    const message = document.getElementById("message");
    const loadingIndicator = document.createElement("div");
    loadingIndicator.id = "loading";
    loadingIndicator.style.display = "none";
    loadingIndicator.innerHTML = "⏳ Processing...";
    downloadButton.parentNode.insertBefore(loadingIndicator, downloadButton.nextSibling);

    function isValidInstagramURL(url) {
        const regex = /https?:\/\/(www\.)?instagram\.com\/(reel|p)\/[a-zA-Z0-9_-]+\/?/;
        return regex.test(url);
    }

    function showMessage(text, isError = false) {
        message.innerText = text;
        message.style.color = isError ? "#ff4444" : "#00C851";
    }

    downloadButton.addEventListener("click", async function () {
        let url = inputField.value.trim();
        console.log("Entered URL:", url);

        if (!url || !isValidInstagramURL(url)) {
            showMessage("⚠️ Please enter a valid Instagram Reel URL!", true);
            return;
        }

        downloadButton.innerText = "Downloading...";
        downloadButton.disabled = true;
        loadingIndicator.style.display = "block";
        message.innerText = "";

        try {
            let response = await fetch("https://reelxtract.onrender.com/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });

            const contentType = response.headers.get("content-type");
            if (!response.ok) {
                if (contentType && contentType.includes("application/json")) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || "Unknown error occurred");
                } else {
                    throw new Error(`Server error: ${response.status}`);
                }
            }

            if (!contentType || !contentType.includes("video/mp4")) {
                throw new Error("Invalid response format from server");
            }

            let blob = await response.blob();
            if (blob.size === 0) {
                throw new Error("Downloaded file is empty");
            }

            let link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = "Instagram_Reel.mp4";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showMessage("✅ Download Complete!");
        } catch (error) {
            console.error("Download Error:", error);
            showMessage(`❌ Error: ${error.message}`, true);
        } finally {
            downloadButton.innerText = "Download";
            downloadButton.disabled = false;
            loadingIndicator.style.display = "none";
        }
    });

    inputField.addEventListener("input", function () {
        downloadButton.innerText = "Download";
        message.innerText = "";
    });
});
