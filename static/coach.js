let steps = [
 {id:"searchBar", title:"Search", text:"Search your product here"},
 {id:"cartIcon", title:"Cart", text:"Items appear here"},
 {id:"checkoutBtn", title:"Checkout", text:"Click to pay"}
];

let step = 0;

function startTutorial(){
  document.getElementById("coachOverlay").style.display="block";
  showStep();
}

function showStep(){
  let el = document.getElementById(steps[step].id);
  let rect = el.getBoundingClientRect();

  highlight.style.top = rect.top+"px";
  highlight.style.left = rect.left+"px";
  highlight.style.width = rect.width+"px";
  highlight.style.height = rect.height+"px";

  coachBox.style.top = (rect.bottom+10)+"px";
  coachBox.style.left = rect.left+"px";

  coachTitle.innerText = steps[step].title;
  coachText.innerText = steps[step].text;
}

function nextStep(){
  step++;
  if(step >= steps.length){
    coachOverlay.style.display="none";
    return;
  }
  showStep();
}