(function(){

    var Helpers = {};

    /**
     * Get all the parents between the target
     * and the event listener. Can be filtered by
     * a DOM query.
     * This is a way to target elements inside an
     * `a`.
     */
    Helpers.getEventPath = function(e, matching) {
        var path = [];
        var el = e.target;
        var include;
        while (el && el !== e.currentTarget) {
            include = (!matching || el.matches(matching)) ? true : false;
            if (include) {
                path.push(el);
            }
            el = el.parentElement;
        }
        return path;
    };


    Helpers.closest = function(el, pattern) {
        var match = el.matches(pattern);
        var result = null;
        while (!match) {
            el = el.parentElement;
            match = el === null || el.matches(pattern); // Null means we're out of parents
            if (match) {
                result = el;
            }
        }
        return el;
    };

    define('cheapskate/helpers', [], function() {
      return Helpers;
    });

})();