var app = angular.module("TestApp", ["ngRoute", "ui.bootstrap", "Controllers"]);

app.config(["$routeProvider", "$interpolateProvider",
    function($routeProvider, $interpolateProvider) {
        $routeProvider
            .when("/gallery", {
                templateUrl: "static/partials/gallery.html",
                controller: "GalleryController"
            })
            .when("/pathfinder", {
                templateUrl: "static/partials/pathfinder.html",
                controller: "PathfinderController"
            })
            .otherwise({
                redirectTo: "/gallery"
            });
            
        // Replace symbols to prevent conflict with Jinja2's template
        $interpolateProvider.startSymbol("[{");
        $interpolateProvider.endSymbol("}]");
    }
]);