angular.module('jhackIt')
    .service('scanStateService', ["$http", "$rootScope", "$interval", function($http, $rootScope, $interval) {

        var scanState;

        $interval(function() {
            return $http.get("/api/get_state").then(function successCallback(response) {
                scanState = JSON.stringify(response.data);
                $rootScope.$broadcast('stateUpdate', {data: scanState});
            }, function failureCallback(reason) {
                console.log(reason);
            })
        }, 5000);

}]);