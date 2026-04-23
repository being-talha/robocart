function updateBill(cartData) {
  const subtotal = Number(cartData.total || 0);
  const tax = subtotal * taxRate; // Aap isko discount logic mein bhi badal sakti hain
  const total = subtotal + tax;

  document.getElementById("subtotal").innerText = formatCurrency(subtotal);
  document.getElementById("grandTotal").innerText = formatCurrency(total);

  // Update Left Side Scanned Rows
  const leftList = document.getElementById("scannedItemsList");
  leftList.innerHTML = "";
  
  // Update Right Side Cart Cards
  const rightList = document.getElementById("cartContainer");
  rightList.innerHTML = "";

  (cartData.items || []).forEach(item => {
    // Left side row (Tea Green)
    leftList.innerHTML += `
      <div class="scanned-row">
        <span>${item.name} x ${item.qty}</span>
        <span>${formatCurrency(item.price * item.qty)}</span>
      </div>
    `;

    // Right side card (Modern style)
    rightList.innerHTML += `
      <div class="cart-card">
        <img src="/static/images/${item.image || 'default.png'}" alt="item">
        <div>
          <div style="font-weight:bold">${item.name}</div>
          <div style="color:var(--midnight-green); font-size:0.9rem">${formatCurrency(item.price)}</div>
        </div>
        <div class="qty-controls">
          <button class="qty-ctrl-btn" onclick="updateQty('${item.barcode}', 'minus')">−</button>
          <span>${item.qty}</span>
          <button class="qty-ctrl-btn" onclick="updateQty('${item.barcode}', 'plus')">+</button>
        </div>
      </div>
    `;
  });
}