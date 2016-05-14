var _ = require("underscore");
var helpers = require("./helpers.js");

class CreditCardChargeFilter {

    constructor(options){
        this.el = options.el;
        this.amountEl = options.amountEl;
        this.setupData();
        this.setupUI();
        this.setupEvents();
        this.syncAmount();
    }

    setupData() {
        this.data = [];
        for (var i = 0; i < this.el.children.length; i++) {
            let option = this.el.children[i];
            let datum = JSON.parse(option.getAttribute("data-json"));
            datum.element = option;
            datum.selected = option.hasAttribute("selected");
            this.data.push(datum);
        }
    }

    setupUI() {
        this.component = document.createElement("div");
        this.component.id = "charge-filter";
        this.component.className = "widget";
        this.el.parentElement.appendChild(this.component);
        var html = this.template({data: this.data});
        this.component.innerHTML = html;

        // Hide original
        this.el.style.display = "none";
    }

    setupEvents() {

        // Select item
        this.component.addEventListener("click", function(e){
            var match = helpers.getEventPath(e, "[data-id]");
            var isLink = helpers.getEventPath(e, "a");
            if (match.length && !isLink.length) {
                match = match[0];
                var id = parseInt(match.getAttribute("data-id"), 10);
                var charge = _.findWhere(this.data, {id: id});
                charge.selected = !charge.selected;
                var option = this.el.querySelector(`option[value="${id}"]`);

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
        this.component.querySelector(".filter").addEventListener("keyup", function(e){
            var rows = this.component.querySelectorAll("tr");
            var query = e.target.value;
            for (var i = 0; i < rows.length; i++) {
                let row = rows[i];
                if (row.textContent.toLowerCase().indexOf(query) === -1) {
                    row.classList.add("hide");
                } else {
                    row.classList.remove("hide");
                }
            }
        }.bind(this));
    }

    syncAmount() {
        var selectedAmounts = _.map(_.where(this.data, {
            selected: true
        }), function(c) {
            return c.amount;
        });
        var sum = _.reduce(selectedAmounts, function(memo, num){
            return memo + num; 
        });

        var diff = sum - this.amountEl.value;
        this.component.querySelector(".status b").textContent = diff.toFixed(2);
    }

    get template() {
        return _.template(`
            <input type="text" placeholder="filter" class="filter" />
            <table class="items">
                <% _.each(data, function(obj){ %>
                    <tr class="<%= obj.selected ? "selected" : "" %>" data-id="<%= obj.id %>">
                        <td><%= obj.title %></td>
                        <td>\$<%= obj.amount %></td>
                        <td><%= obj.category %></td>
                        <td><%= obj.date %></td>
                        <td><a href="<%= obj.url %>" target="_blank"><i class="fa fa-chevron-circle-right"></i></a></td>
                    </tr>
                <% }); %>
            </table>
            <p class="status"><b></b> remaining</p>
        `);
    }

}


let el = document.querySelector("[data-credit-card-charge-filter]");
if (el) {
    var creditCardChargeFilter = new CreditCardChargeFilter({
        el: el, 
        amountEl: document.getElementById("id_amount")
    });
}

module.exports = {
    Component: CreditCardChargeFilter,
}
