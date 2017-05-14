// 
// Get all the parents between the target
// and the event listener. Can be filtered by
// a DOM query.
// This is a way to target elements inside an
// `a`.
// 
export function getEventPath(e, matching) {
    let path = [];
    let el = e.target;
    let include;
    while (el && el !== e.currentTarget) {
        include = (!matching || el.matches(matching)) ? true : false;
        if (include) {
            path.push(el);
        }
        el = el.parentElement;
    }
    return path;
};


export function closest (el, pattern) {
    let match = el.matches(pattern);
    let result = null;
    while (!match) {
        el = el.parentElement;
        match = el === null || el.matches(pattern); // Null means we're out of parents
        if (match) {
            result = el;
        }
    }
    return el;
};

