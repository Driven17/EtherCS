document.getElementById("save-api-key").addEventListener("click", async () => {
    const apiKey = document.getElementById("steam-api-key").value;

    const response = await fetch("/api/me/save-settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            setting: "steam_api_key",
            value: apiKey,
        }),
    });

    const result = await response.json();
    document.getElementById("settings-message").innerText = result.message;
});

document.getElementById("save-trade-link").addEventListener("click", async () => {
    const tradeUrl = document.getElementById("trade-link").value;

    const response = await fetch("/api/me/save-settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            setting: "trade_link",
            value: tradeUrl,
        }),
    });

    const result = await response.json();
    document.getElementById("settings-message").innerText = result.message;
});

document.getElementById("connect-wallet-button").addEventListener("click", async () => {
    if (typeof window.ethereum !== "undefined") {
        try {
            const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
            const walletAddress = accounts[0];
            document.getElementById("wallet-address").innerText = `Connected: ${walletAddress}`;
            
            await fetch("/api/me/save-settings", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    setting: "wallet_address",
                    value: walletAddress 
                }),
            });
            
        } catch (error) {
            console.error("User denied connection or error occurred", error);
            document.getElementById("wallet-address").innerText = "Connection failed.";
        }
    } else {
        alert("MetaMask is not installed.");
    }
});

// all code for opening new windows - for "To get" buttons //

function openControlledWindow(url) {
    const name = "MyWindow";
    const features = "width=600,height=800,menubar=no,toolbar=no,location=no,status=no,resizable=no,scrollbars=yes";

    window.open(url, name, features);
}

document.getElementById("get-api-key").addEventListener("click", function(event) {
    event.preventDefault();
    openControlledWindow("https://steamcommunity.com/dev/apikey");
});

document.getElementById("get-trade-link").addEventListener("click", function(event) {
    event.preventDefault();
    openControlledWindow("http://steamcommunity.com/my/tradeoffers/privacy#trade_offer_access_url");
});