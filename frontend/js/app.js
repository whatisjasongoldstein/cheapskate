import './widgets';
import CreditCardChargeFilter from './credit-card-admin';
import handleKeyboard from './keyboard-shortcuts';


// Credit Card Filters
let el = document.querySelector("[data-credit-card-charge-filter]");
if (el) {
    let creditCardChargeFilter = new CreditCardChargeFilter({
        el: el, 
        amountEl: document.getElementById("id_amount")
    });
}

// Keyboard shortcuts
window.addEventListener('keyup', handleKeyboard, false);

