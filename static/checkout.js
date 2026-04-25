let steps = [
  {
    id: "barcode",
    title: "Scan Products 🔍",
    text: "Scan barcode to add products automatically"
  },
  {
    id: "productImage",
    title: "Product View 🖼",
    text: "Here you can see scanned item details"
  },
  {
    id: "cartIcon",
    title: "Your Cart 🛒",
    text: "All selected items appear here"
  },
  {
    id: "checkoutBtn",
    title: "Checkout 💳",
    text: "Click here to complete payment"
  }
];

let step = 0;

function startTutorial(){
  document.getElementById("coachOverlay").style.display="block";
  step = 0;
  showStep();
}

function showStep(){
  let el = document.getElementById(steps[step].id);
  let rect = el.getBoundingClientRect();

  highlight.style.top = rect.top + "px";
  highlight.style.left = rect.left + "px";
  highlight.style.width = rect.width + "px";
  highlight.style.height = rect.height + "px";

  coachBox.style.top = rect.bottom + 10 + "px";
  coachBox.style.left = rect.left + "px";

  coachTitle.innerText = steps[step].title;
  coachText.innerText = steps[step].text;
}

function nextStep(){
  step++;
  if(step >= steps.length){
    document.getElementById("coachOverlay").style.display="none";
    return;
  }
  showStep();
}