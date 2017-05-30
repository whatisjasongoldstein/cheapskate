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
    .reduce((total, current) => total + current, 0);

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
                  <svg width="1792" height="1792" viewBox="0 0 1792 1792" 
                    xmlns="http://www.w3.org/2000/svg"><path d="M1280 896q0 14-9 23l-320 
                    320q-9 9-23 9-13 0-22.5-9.5t-9.5-22.5v-192h-352q-13 
                    0-22.5-9.5t-9.5-22.5v-192q0-13 9.5-22.5t22.5-9.5h352v-192q0-14 
                    9-23t23-9q12 0 24 10l319 319q9 9 9 23zm160 
                    0q0-148-73-273t-198-198-273-73-273 73-198 198-73 273 73 
                    273 198 198 273 73 273-73 198-198 73-273zm224 0q0 209-103 
                    385.5t-279.5 279.5-385.5 103-385.5-103-279.5-279.5-103-385.5 
                    103-385.5 279.5-279.5 385.5-103 385.5 103 
                    279.5 279.5 103 385.5z"/></svg>
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