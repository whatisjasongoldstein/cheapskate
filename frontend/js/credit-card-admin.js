import {getEventPath} from "./helpers";

export default function CreditCardChargeFilter(options) {
  this.el = options.el;
  this.amountEl = options.amountEl;
  this.setupData();
  this.setupUI();
  this.setupEvents();
  this.syncAmount();
}

CreditCardChargeFilter.prototype.setupData = function() {
  this.data = [];
  for (let i = 0; i < this.el.children.length; i++) {
    let option = this.el.children[i];
    let datum = JSON.parse(option.getAttribute("data-json"));
    datum.element = option;
    datum.selected = option.hasAttribute("selected");
    this.data.push(datum);
  }
}

CreditCardChargeFilter.prototype.setupUI = function() {
  this.component = document.createElement("div");
  this.component.id = "charge-filter";
  this.component.className = "widget";
  this.el.parentElement.appendChild(this.component);
  this.component.innerHTML = this.render({
    items: this.data
  });

  // Hide original
  this.el.style.display = "none";
}

CreditCardChargeFilter.prototype.setupEvents = function() {

  // Select item
  this.component.addEventListener("click", function(e) {
    let match = getEventPath(e, "[data-id]")[0];
    let isLink = getEventPath(e, "a")[0];
    if (match && !isLink) {
      let id = parseInt(match.getAttribute("data-id"), 10);
      let charge = this.data.filter((d) => d.id === id)[0];

      charge.selected = !charge.selected;
      let option = this.el.querySelector(`option[value="${id}"]`);

      option.selected = charge.selected;
      if (charge.selected) {
        match.classList.add("selected");
      } else {
        match.classList.remove("selected");
      }

      // Update amount needed
      this.syncAmount();
    }
  }.bind(this));

  // Updating Filtering
  this.component.querySelector(".filter").addEventListener("keyup", function(e) {
    let rows = this.component.querySelectorAll("tr");
    let query = e.target.value;
    for (let i = 0; i < rows.length; i++) {
      let row = rows[i];
      if (row.textContent.toLowerCase().indexOf(query) === -1) {
        row.classList.add("hide");
      } else {
        row.classList.remove("hide");
      }
    }
  }.bind(this));
}

CreditCardChargeFilter.prototype.syncAmount = function() {
  let sum = this.data.filter((d) => d.selected === true)
    .map((d) => d.amount)
    .reduce((total, current) => total + current);

  let diff = sum - this.amountEl.value;
  this.component.querySelector(".status b").textContent = diff.toFixed(2);
}

CreditCardChargeFilter.prototype.render = function(context) {
  let items = context.items;
  return `
    <input type="text" placeholder="filter" class="filter" />
    <table class="items">
      ${ items.map((obj)=>{
         return `
           <tr class="${ obj.selected ? "selected" : "" }" data-id="${ obj.id }">
             <td>${ obj.title }</td>
             <td>$${ obj.amount.toFixed(2) }</td>
             <td>${ obj.category }</td>
             <td>${ obj.date }</td>
             <td>
               <a href="${ obj.url }" target="_blank">
                 <i class="fa fa-chevron-circle-right"></i>
               </a>
             </td>
           </tr>
         `
      }).join("") }
    </table>
    <p class="status"><b></b> remaining</p>
  `;
}


let el = document.querySelector("[data-credit-card-charge-filter]");
if (el) {
    let creditCardChargeFilter = new CreditCardChargeFilter({
        el: el, 
        amountEl: document.getElementById("id_amount")
    });
}

// export default l component = CreditCardChargeFilter;