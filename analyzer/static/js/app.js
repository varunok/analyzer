var parserApp = angular.module('parserApp', ['ngRoute', 'ngSanitize', 'angular-loading-bar']);



parserApp.config(function($routeProvider) {
    $routeProvider
    .when("/admin", {
        template : adminTmp,
        controller : "administratorAppController"
    })
    .when("/", {
        template : parserTmp,
        // controller : "administratorAppController"
    })
    .when("/admin/create", {
        template : adminCreateTmp,
        controller : "administratorCreateAppController"
    });
});

angular.module('parserApp')
    .config(function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

angular.module('parserApp')
    .config(function(cfpLoadingBarProvider) {
        cfpLoadingBarProvider.includeSpinner = true;
    });

parserApp.controller("administratorAppController", function($scope, $location, $http, cfpLoadingBar) {

    $scope.start = function () {
        cfpLoadingBar.start();
    };

    $scope.complete = function () {
        cfpLoadingBar.complete();
    };
    $http.get('api/v1.0/users')
        .then(function(response) {
            $scope.users = response.data.results;
            $scope.total_pages = response.data.total_pages;
    });
});

parserApp.controller("administratorCreateAppController", function($scope, $location, $http, cfpLoadingBar) {
    $scope.user = {
        // first_name: ''
    };
    $scope.save = function () {
        $http.post('api/v1.0/users/', $scope.user)
            .then(function(response) {
                $scope.status = response.status;
                $scope.data = response.data;
                $scope.error_username = false;
                $scope.error_password = false;
                $scope.error_email = false;
                $scope.error_password2 = false;
            }, function(response) {
                console.log(response.data);
                if (response.data.username){
                    $scope.error_username = response.data.username[0];
                }else{
                    $scope.error_username = false;
                }
                if (response.data.password){
                    $scope.error_password = response.data.password[0];
                }else{
                    $scope.error_password = false;
                }
                if (response.data.password2){
                    $scope.error_password2 = response.data.password2[0];
                }else{
                    $scope.error_password2 = false;
                }
                if (response.data.email){
                    $scope.error_email = response.data.email[0];
                }else{
                    $scope.error_email = false;
                }
                $scope.status = response.status;
            });
    };
});