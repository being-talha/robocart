let selectedMethod = "easypaisa";
let qrInstance = null;
let timeLeft = 299;
let timerInterval = null;

function formatAmount(value) {
  const numeric = Number(value) || 0;
  return `Rs ${numeric.toFixed(2).replace(/\.00$/, "")}`;
}

function generateReference() {
  return "TXN-" + Math.floor(100000 + Math.random() * 900000);
}

function getAmountNumber() {
  return Number(window.checkoutData?.grandTotal || 0);
}

function getPaymentPayload() {
  return JSON.stringify({
    merchant: "RoboCart Smart Store",
    order_ref: window.checkoutData?.orderRef || "",
    provider: selectedMethod,
    amount: getAmountNumber(),
    currency: "PKR",
    items: window.checkoutData?.items || [],
    reference: document.getElementById("referenceId").innerText,
    created_at: new Date().toISOString()
  });
}

function renderQR() {
  const qrContainer = document.getElementById("qrcode");
  qrContainer.innerHTML = "";

  qrInstance = new QRCode(qrContainer, {
    text: getPaymentPayload(),
    width: 190,
    height: 190
  });
}

function setStatus(label, className) {
  const statusEl = document.getElementById("paymentStatus");
  statusEl.innerText = label;
  statusEl.className = className;
}

function selectMethod(method) {
  selectedMethod = method;

  const easyBtn = document.getElementById("easyBtn");
  const jazzBtn = document.getElementById("jazzBtn");
  const selectedMethodTitle = document.getElementById("selectedMethodTitle");
  const selectedMethodText = document.getElementById("selectedMethodText");

  easyBtn.classList.remove("active");
  jazzBtn.classList.remove("active");

  if (method === "easypaisa") {
    easyBtn.classList.add("active");
    selectedMethodTitle.innerText = "EasyPaisa QR";
    selectedMethodText.innerText = "EasyPaisa";
  } else {
    jazzBtn.classList.add("active");
    selectedMethodTitle.innerText = "JazzCash QR";
    selectedMethodText.innerText = "JazzCash";
  }

  document.getElementById("referenceId").innerText = generateReference();
  resetTimer();
  renderQR();
}

function updateTimerDisplay() {
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  document.getElementById("qrTimer").innerText =
    String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
}

function startTimer() {
  clearInterval(timerInterval);

  timerInterval = setInterval(() => {
    if (timeLeft > 0) {
      timeLeft--;
      updateTimerDisplay();
    } else {
      clearInterval(timerInterval);
      setStatus("Expired", "expired");
    }
  }, 1000);
}

function resetTimer() {
  timeLeft = 299;
  setStatus("Pending", "pending");
  updateTimerDisplay();
  startTimer();
}

function refreshQR() {
  document.getElementById("referenceId").innerText = generateReference();
  resetTimer();
  renderQR();
}

function goBack() {
  window.location.href = "/shop";
}

function downloadBill() {
  const orderRef = window.checkoutData?.orderRef || "";
  const items = window.checkoutData?.items || [];
  const subtotal = window.checkoutData?.subtotal || 0;
  const tax = window.checkoutData?.tax || 0;
  const grandTotal = window.checkoutData?.grandTotal || 0;
  const selectedMethodText = document.getElementById("selectedMethodText").innerText;
  const referenceId = document.getElementById("referenceId").innerText;
  const paymentStatus = document.getElementById("paymentStatus").innerText;

  const receiptText = `
RoboCart Smart Store
Self Checkout Terminal

Order Ref: ${orderRef}
Date: ${document.getElementById("billDate").innerText}
Time: ${document.getElementById("billTime").innerText}

Items:
${items.map(item => `${item.name} (${item.qty} x Rs ${item.price}) = Rs ${item.subtotal}`).join("\n")}

Subtotal: ${formatAmount(subtotal)}
Tax: ${formatAmount(tax)}
Total: ${formatAmount(grandTotal)}

Payment Method: ${selectedMethodText}
Reference ID: ${referenceId}
Status: ${paymentStatus}
`;

  const blob = new Blob([receiptText], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `bill-${orderRef}.txt`;
  link.click();
}

function completePayment() {
  if (document.getElementById("paymentStatus").innerText === "Expired") {
    alert("QR expired. Please refresh QR and try again.");
    return;
  }

  fetch("/complete-checkout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      payment: selectedMethod
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "success") {
        clearInterval(timerInterval);
        setStatus("Paid", "paid");
        alert(`Payment successful! Order ID: ${data.order_id}`);
        window.location.href = "/shop";
      } else if (data.status === "empty") {
        alert("Cart is empty.");
      } else {
        alert(data.message || "Payment failed.");
      }
    })
    .catch(err => {
      console.error("Checkout error:", err);
      alert("Something went wrong while completing payment.");
    });
}

window.onload = function () {
  document.getElementById("payableAmount").innerText = formatAmount(getAmountNumber());
  document.getElementById("referenceId").innerText = generateReference();
  renderQR();
  resetTimer();
};