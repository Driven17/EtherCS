/* Extension ID for EtherCS, used to send messages to the background script */
const EXTENSION_ID = "knfiljkpnoalgndfebfmninnafckckbf";

/*
  Checks if the EtherCS extension is installed and responding.
  Calls the provided callback with a boolean indicating installation status
  and the extension's response if available.
*/
function checkExtensionInstalled(callback) {
  chrome.runtime.sendMessage(EXTENSION_ID, { type: "ping_extension" }, response => {
    const isInstalled = !chrome.runtime.lastError && response?.status === 200;
    callback(isInstalled, response);
  });
}

/*
  Sends a fetch request to the specified URL (defaults to POST),
  optionally with a JSON body, then reloads the page on completion.
*/
async function reloadOnCompletion(url, method = "POST", body = null) {
  await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    ...(body && { body: JSON.stringify(body) })
  }).then(() => window.location.reload());
}

/* 
  Handle Accept Trade button clicks:
  - Checks if the extension is installed.
  - If installed, calls backend API to accept trade.
  - Reloads the page after backend call.
*/
document.querySelectorAll(".accept-trade-btn").forEach(button => {
  button.addEventListener("click", () => {
    const transactionId = button.dataset.id;

    checkExtensionInstalled(isInstalled => {
      if (!isInstalled) {
        alert("You need the EtherCS extension installed to accept this sale.");
        return;
      }

      reloadOnCompletion(`/api/accept-trade/${transactionId}`);
    });
  });
});

/* 
  Handle Send Trade button clicks:
  - Checks if the extension is installed.
  - Fetches trade details from backend.
  - Sends a trade offer using the extension.
  - If the trade requires confirmation, prompts user to confirm.
  - Sends response status to backend and reloads page.
*/
document.querySelectorAll(".send-trade-btn").forEach(button => {
  button.addEventListener("click", async () => {
    const transactionId = button.dataset.id;

    checkExtensionInstalled(async (isInstalled) => {
      if (!isInstalled) {
        alert("You need the EtherCS extension installed to send this trade.");
        return;
      }

      try {
        const res = await fetch(`/api/get-trade-payload/${transactionId}`);
        const tradePayload = await res.json();
        if (!tradePayload.success) throw new Error("Failed to get trade details.");

        const {
          item_assetid,
          buyer_steam_id,
          buyer_trade_token,
          message
        } = tradePayload.payload;

        chrome.runtime.sendMessage(
          EXTENSION_ID,
          {
            type: "send_trade_offer",
            payload: {
              toSteamID64: buyer_steam_id,
              tradeToken: buyer_trade_token,
              message,
              assetIDsToGive: [item_assetid],
              assetIDsToReceive: [],
              forceEnglish: false
            }
          },
          async (response) => {
            console.log("Trade offer response:", response);

            const needsConfirmation = response?.json?.needs_mobile_confirmation || response?.json?.needs_email_confirmation;
            let proceed = true;

            /*
              Later on will ping the extension
              to check if user has confirmed the
              trade offer through mobile/email
            */
            if (needsConfirmation) {
              proceed = confirm("You need to confirm the trade in your Steam app or email. Click OK after confirming.");
            }

            if (proceed) {
              await reloadOnCompletion("/api/send-trade-response", "POST", {
                transaction_id: transactionId,
                status: response.status === 200 ? "success" : "error",
                trade_offer_id: response?.json?.tradeofferid || null,
                error: response?.error || null
              });
            }
          }
        );
      } catch (err) {
        alert(err.message);
      }
    });
  });
});