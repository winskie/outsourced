angular.module("Controllers", ["Services"])

.controller("MainController", ["$scope", "$location",
    function($scope, $location) {
        $scope.getView = function(viewLocation) {
            return viewLocation == $location.path();
        }
    }
])

.controller("GalleryController", ["$scope", "$window", "Utilities", "LocalStorage", "Flickr",
    function($scope, $window, Utilities, LocalStorage, Flickr) {
        // This is necessary as we cannot change the callback function
        // returned by the Flickr API
        $window.jsonFlickrFeed = function(response) {
            var data = Flickr.callback(response);

            for(var i = 0; i < data.length; i++) {
                $scope.addPhoto(data[i], 'public');
            }

            $scope.photosLoading = false;
        };
        
        // Loads the current user or create a new user.
        // This is just a simple web application, no need to setup
        // a full fledged user management module.
        var user = LocalStorage.get("user", false);
        if (!user) {
            user = Utilities.randomString(10);
            LocalStorage.set("user", user);
        }
        $scope.user = user;

        $scope.title = "Photo Gallery";
        $scope.photos = [];
        $scope.likedPhotos = [];
        $scope.query = null;
        $scope.photosLoading = false;
        $scope.searchbox = "";
        $scope.view = "Public Feed";

        $scope.clearPhotos = function() {
            $scope.photos = [];
        }

        // Load photos from public feed
        $scope.loadPublicFeedPhotos = function() {
            $scope.photosLoading = true;
            Flickr.getPhotos();
        }
        
        // Load liked photos from the database
        $scope.loadLikedPhotos = function() {
            Flickr.getLikedPhotos($scope.user).then(
                function(response) {
                    var photos = response.data.photos;
                    var n = photos.length;
                    $scope.likedPhotos = [];
                    for(var i = 0; i < n; i++) {
                        photos[i].favorite = true;
                        $scope.addPhoto(photos[i], "liked");
                    }
                },
                function(reason) {
                    console.error(reason);
                });
        }

        // Tag search
        $scope.search = function($event) {
            if (($event.which == 13 && $event.type == "keypress") ||
                    ($event.type == "click")) {
                var query = $scope.searchbox;
                if (query) {
                    $scope.view = "Search Result";
                    $scope.query = query;
                    $scope.searchbox = null;
                    $scope.clearPhotos();
                    Flickr.getPhotos(query);
                } else {
                    $scope.showPublicFeed();
                }
            }
        }
        
        // Switch to Public Feed view
        $scope.showPublicFeed = function(reload) {
            // Mandatory reload of public feed if coming from search result view
            if ($scope.query) {
                reload = true;
                $scope.query = null;
            }
            
            $scope.view = "Public Feed";
            if (reload) {
                $scope.clearPhotos();
                $scope.loadPublicFeedPhotos();    
            }
        }

        // Switch to Liked Photos view
        $scope.showLikedPhotos = function(reload) {
            $scope.view = "Liked Photos";
            if (reload) {
                $scope.loadLikedPhotos();
            }
        }

        // Add photo to a gallery, i.e. public or liked
        $scope.addPhoto = function(photoData, gallery) {
            if (gallery == "public") {
                $scope.photos.push(photoData);    
            } else if (gallery == "liked") {
                $scope.likedPhotos.push(photoData);
            }
        }

        // Toggle like status of a photo
        $scope.like = function(photo, $event) {
            Flickr.likePhoto($scope.user, photo).then(
                function(response) {
                    if (response.action == "liked") {
                        var copyOfPhoto = angular.copy(photo);
                        copyOfPhoto.seq = response.id;
                        $scope.likedPhotos.push(copyOfPhoto);
                    } else {
                        var index = $scope.likedPhotos.indexOf(photo);
                        $scope.likedPhotos.splice(index, 1);
                        
                        // Remove liked status from the Public Feed just in case
                        // the same image is in there
                        if ($scope.view == 'Liked Photos') {
                            for (var i = 0; i < $scope.photos.length; i++) {
                                if ($scope.photos[i].photoUrl == photo.photoUrl) {
                                    $scope.photos[i].favorite = false;
                                    break;
                                }
                            }
                        }
                    }
                },
                function(reason) {
                    console.error(reason);
                }
            )

            if (photo.favorite) {
                photo.favorite = !photo.favorite;
            } else {
                photo.favorite = true;
            }
        }
        
        // Scroll back to top of the page
        $scope.scrollToTop = function() {
            $window.scrollTo(0,0);
        }

        // load initial set of photos
        $scope.showPublicFeed(true);
        $scope.loadLikedPhotos();
    }
])

.controller("PathfinderController", ["$scope", "Pathfinder",
    function($scope, Pathfinder) {
        $scope.title = "Pathfinder";
        
        $scope.minRows = 2;
        $scope.minCols = 2;
        $scope.maxRows = 20;
        $scope.maxCols = 20;
        
        $scope.rows = 10;
        $scope.cols = 20;
        $scope.minValue = 1;
        $scope.maxValue = 1000;

        $scope.origin = {"x": 0, "y": 0};
        $scope.destination = {"x": $scope.cols - 1, "y": $scope.rows - 1};
        $scope.moveset = "udlr";
        $scope.grid = [];
        $scope.path = [];
        
        $scope.getRange = function(min, max) {
            var range = [];
            for (var i = min; i <= max; i++) {
                range.push(i);
            }
            return range;
        }

        $scope.generateTerrain = function(callback) {
            Pathfinder.generateTerrain($scope.cols, $scope.rows,
                    $scope.minValue, $scope.maxValue)
                .then(
                    function(response) {
                        var grid = response.grid;
                        $scope.grid = grid;
                        $scope.destination = {"x": $scope.cols - 1, "y": $scope.rows - 1};
                        
                        // Generate terrain data from grid values
                        var terrain = [];
                        for (var i = 0; i < $scope.rows; i++) {
                            var tiles = [];
                            for (var j = 0; j < $scope.cols; j++) {
                                tiles.push({
                                    cost: grid[i][j],
                                    isPath: false
                                });
                            }
                            terrain.push(tiles);
                        }
                        
                        $scope.terrain = terrain;
                        
                        // This doesn't look right, perhaps we can
                        // chain promises here?
                        if (callback) callback();
                    },
                    function(reason) {
                        console.error(reason);
                    }
                );
        }

        $scope.findPath = function() {
            // Don't forget to clear the previous path data,
            // this is a brute force method and should be
            // replaced with a more efficient method
            for (var i = 0; i < $scope.rows; i++) {
                for (var j = 0; j < $scope.cols; j++) {
                    $scope.terrain[i][j].isPath = false;
                }
            }
            
            Pathfinder.findPath($scope.grid, $scope.origin,
                    $scope.destination, $scope.moveset)
                .then(
                    function(response) {
                        var path = response.path;
                        var n = path.length;
                        
                        for (var i = 0; i < n; i++) {
                            $scope.terrain[path[i][1]][path[i][0]].isPath = true;
                        }
                        
                        $scope.directions = response.directions.join(", ");
                    },
                    function(reason) {
                        console.error(reason);
                    }
                );
        }

        $scope.generateTerrain($scope.findPath);
    }
]);