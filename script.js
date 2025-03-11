document.addEventListener("DOMContentLoaded", function () {
    const downloadButton = document.getElementById("download-btn");
    const inputField = document.getElementById("url");
    const message = document.getElementById("message");

    function isValidInstagramURL(url) {
        const regex = /https?:\/\/(www\.)?instagram\.com\/(reel|p)\/[a-zA-Z0-9_-]+\/?/;
        return regex.test(url);
    }

    downloadButton.addEventListener("click", async function () {
        let url = inputField.value.trim();
        console.log("Entered URL:", url);  // Debugging output

        if (!url || !isValidInstagramURL(url)) {
            message.innerText = "⚠️ Please enter a valid Instagram Reel URL!";
            return;
        }

        downloadButton.innerText = "Downloading...";
        downloadButton.disabled = true;
        message.innerText = "";

        try {
            let response = await fetch("https://reelxtract.onrender.com/download", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                let errorText = await response.json();
                throw new Error(errorText.error || "Unknown error");
            }

            let blob = await response.blob();

            // Ensure it's an MP4 file
            if (blob.type !== "video/mp4") {
                throw new Error("Invalid file type received.");
            }

            let link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = "Instagram_Reel.mp4";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            message.innerText = "✅ Download Complete!";
        } catch (error) {
            message.innerText = `❌ Error: ${error.message}`;
            console.error("Download Error:", error);
        } finally {
            downloadButton.innerText = "Download";
            downloadButton.disabled = false;
        }
    });

    // Reset button text when user edits input field
    inputField.addEventListener("input", function () {
        downloadButton.innerText = "Download";
    });
});
