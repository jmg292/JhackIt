angular.module("jhackIt")
    .controller('scanStateController', ["$scope", "$http", "$interval", "$rootScope", "scanStateService", function($scope, $rootScope, $interval) {

        var self = this;

        $interval(function() {
            $('.tabs').tabs();
        }, 1000);

        $scope.interface = "Unknown";
        $scope.target_client = "None";
        $scope.target_essid = "None";
        $scope.target_bssid = "None";
        $scope.monitor_enabled = "No";
        $scope.scanned_bssids = [];
        $scope.scan_data = {}

        $scope.$watch('scan_data', function(scan_data) {
            console.log("Got scan_data change.");
        }, true);

        $scope.$on('stateUpdate', function(event, args) {
            scanned_data = JSON.parse(args.data);
            $scope.interface = scanned_data.using_interface;
            $scope.monitor_enabled = scanned_data.monitor_enabled;

            if(scanned_data.target_client !== null) {
                $scope.target_client = scanned_data.target_client;
            } else {
                $scope.target_client = "None";
            }
            if(scanned_data.target_essid !== null) {
                $scope.target_essid = scanned_data.target_essid;
            } else {
                $scope.target_essid = "None";
            }
            if(scanned_data.target_bssid !== null) {
                $scope.target_bssid = scanned_data.target_bssid;
            } else {
                $scope.target_bssid = "None";
            }

            var new_bssid_cache = [];
            var cached_bssids = $scope.scanned_bssids;

            for(var scanned_bssid in scanned_data.scan_results) {
                if(!(new_bssid_cache.includes(scanned_bssid))) {
                    new_bssid_cache.push(scanned_bssid);
                }
            }
            self.removeUnusedCards(new_bssid_cache, cached_bssids);

            $scope.scanned_bssids = new_bssid_cache;
            $scope.scan_data = scanned_data.scan_results;
        });

        self.removeUnusedCards = function(new_bssid_list, current_bssid_list) {
            for(var bssid_index in current_bssid_list) {
                var bssid = current_bssid_list[bssid_index];
                if(!new_bssid_list.includes(bssid)) {
                    console.log(bssid);
                    var bssidCard = document.getElementById(bssid.replace(new RegExp(':', 'g'), "-") + "-card");
                    if(typeof(bssidCard) !== "undefined" && bssidCard !== null) {
                        bssidCard.parentNode.removeChild(bssidCard);
                    }
                }
            }
        };

        self.acquireTarget = function(ap, client=null) {
            commandData = {
                "type": "acquire_target",
                "bssid": ap,
            }
            if(client !== null) {
                commandData["client"] = client
            }

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/command", true);

            xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
            xhr.send(JSON.stringify(commandData));
            xhr.onloadend = function() {
                console.log("XHR acquire_target command sent successfully.");
            }
        };

        self.clearTarget = function() {
            commandData = {
                "type": "clear_target"
            }

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/command", true);

            xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
            xhr.send(JSON.stringify(commandData));
            xhr.onloadend = function() {
                console.log("XHR clear_target command sent successfully.");
            }
        }

        self.launchDeauths = function(client=null) {
            commandData = {
                "type": "launch_deauths",
            }
            if(client !== null) {
                commandData["client"] = client
            }

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/command", true);

            xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
            xhr.send(JSON.stringify(commandData));
            xhr.onloadend = function() {
                console.log("XHR launch_deauths command sent successfully.");
            }
        }

        self.isTargetingSomething = function() {
            var returnValue = false;
            if($scope.target_client !== "None") {
                returnValue = true;
            } else if ($scope.target_bssid !== "None") {
                returnValue = true;
            }
            return returnValue;
        }

}]);