let selectedPaymentMethod = "easypaisa";
let statusInterval = null;
let hasShownFinalStatusPopup = false;

document.addEventListener("DOMContentLoaded", function () {
  startPaymentStatusPolling();
});

function selectMethod(method) {
  selectedPaymentMethod = method;

  const easyBtn = document.getElementById("easyBtn");
  const jazzBtn = document.getElementById("jazzBtn");
  const cardBtn = document.getElementById("cardBtn");

  const selectedMethodText = document.getElementById("selectedMethodText");
  const qrImage = document.getElementById("paymentQrImage");
  const manualBox = document.querySelector(".manual-payment-box");
  const mockCardBox = document.getElementById("mockCardBox");

  easyBtn.classList.remove("active");
  jazzBtn.classList.remove("active");
  cardBtn.classList.remove("active");

  qrImage.style.display = "block";
  manualBox.style.display = "flex";
  mockCardBox.style.display = "none";

  if (method === "easypaisa") {
    easyBtn.classList.add("active");
    selectedMethodText.textContent = "EasyPaisa";
    qrImage.src = "/static/payments/easypaisa-qr.png";
  }

  if (method === "jazzcash") {
    jazzBtn.classList.add("active");
    selectedMethodText.textContent = "JazzCash";
    qrImage.src = "/static/payments/jazzcash-qr.png";
  }

  if (method === "card") {
    cardBtn.classList.add("active");
    selectedMethodText.textContent = "Debit / Credit Card";
    qrImage.style.display = "none";
    manualBox.style.display = "none";
    mockCardBox.style.display = "flex";
  }
}

async function submitPaymentInfo() {
  const senderNumber = document.getElementById("senderNumber").value.trim();

  if (!senderNumber) {
    showPopup("Please enter sender mobile number.", "Missing Information");
    return;
  }

  try {
    const response = await fetch(window.checkoutData.submitPaymentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        orderRef: window.checkoutData.orderRef,
        paymentMethod: selectedPaymentMethod,
        senderNumber: senderNumber,
        amount: window.checkoutData.grandTotal
      })
    });

    const data = await response.json();

    showPopup(data.message, data.success ? "Payment Submitted" : "Payment Notice");

    if (data.success) {
      setPaymentStatus("Pending Verification", "pending");
    }
  } catch (error) {
    showPopup("Something went wrong while submitting payment information.", "Error");
  }
}

async function checkPaymentStatus() {
  try {
    const response = await fetch(window.checkoutData.statusUrl);
    const data = await response.json();

    if (data.status === "PAID") {
      setPaymentStatus("Paid", "paid");
      clearInterval(statusInterval);
      window.location.href = "/thankyou/" + window.checkoutData.orderRef;
      return;
    }

    if (data.status === "REJECTED") {
      setPaymentStatus("Rejected", "failed");
      clearInterval(statusInterval);

      if (!hasShownFinalStatusPopup) {
        hasShownFinalStatusPopup = true;
        showPopup("Payment rejected. Please contact support.", "Payment Rejected");
      }

      return;
    }

    if (data.status === "PENDING_VERIFICATION") {
      setPaymentStatus("Pending Verification", "pending");
      return;
    }

    setPaymentStatus("Pending Payment", "pending");

  } catch (error) {
    console.error("Payment status check failed:", error);
  }
}

function startPaymentStatusPolling() {
  checkPaymentStatus();
  statusInterval = setInterval(checkPaymentStatus, 5000);
}

function setPaymentStatus(text, className) {
  const status = document.getElementById("paymentStatus");
  status.textContent = text;
  status.className = className;
}

function showPopup(message, title = "Notice") {
  document.getElementById("customModalTitle").textContent = title;
  document.getElementById("customModalMessage").textContent = message;
  document.getElementById("customModal").classList.add("show");
}

function closeCustomModal() {
  document.getElementById("customModal").classList.remove("show");
}

function goBack() {
  window.location.href = "/cart";
}

function downloadBill() {
  window.print();
}