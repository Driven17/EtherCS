document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".buy-button");

    buttons.forEach(button => {
        button.addEventListener("click", async () => {
            const listingId = button.dataset.listingId;

            // Placeholder for payment via wallet (to be filled later)
            const paymentSuccess = await mockPaymentProcess();

            if (!paymentSuccess) {
                alert("Payment failed.");
                return;
            } else {
                const response = await finalizePurchase(listingId)
            }
        });
    });
});

// Temporary fake/mock payment processor (always returns success)
async function mockPaymentProcess() {
    // TODO: Replace with actual Web3 wallet interaction later
    return new Promise(resolve => {
        setTimeout(() => resolve(true), 300); // Simulate a small delay
    });
}

async function finalizePurchase(listingId) {
    // On successful payment, notify backend
    await fetch("/api/buy-listing", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ listing_id: listingId })
    })

    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Purchase successful!");
            location.reload();
        } else {
            alert("Purchase failed: " + data.message);
        }
    });
}