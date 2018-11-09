angular.module("jhackIt")
    .filter('disabledFilter', function() {
      return function(isTargetingSomething) {
        var out = '';
        if(isTargetingSomething) {
            out = '';
        }
        return out;
      };
})