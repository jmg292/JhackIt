angular.module("jhackIt")
    .filter('cleanColon', function() {
      return function(input) {
        input = input || '';
        var out = '';
        out = input.replace(new RegExp(':', 'g'), "-");
        return out;
      };
})