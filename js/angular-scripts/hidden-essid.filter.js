angular.module("jhackIt")
    .filter('hiddenEssid', function() {
      return function(input) {
        input = input || '<Hidden>';
        var out = '';
        if(input.includes("\\x00\\x00")) {
            out = "<Hidden>";
        } else {
            out = input;
        }
        return out;
      };
})