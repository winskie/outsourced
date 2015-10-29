angular.module("Services", [])

.factory("Utilities", [
    function() {
        return {
            randomString: function(length) {
                var str = "";
                var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+abcdefghijklmnopqrstuvwxyz01234567890-=";
                
                if (!length) length = 10;
                for (var i = 0; i < length; i++) {
                    str += chars.charAt(Math.floor(Math.random()*chars.length));
                }
                
                return str;
            }
        }
    }
])

.factory('LocalStorage', ["$window",
    function($window) {
        return {
            set: function(key, value) {
                $window.localStorage[key] = value;
            },
            get: function(key, defaultValue) {
                return $window.localStorage[key] || defaultValue;
            },
            setObject: function(key, value) {
                $window.localStorage[key] = JSON.stringify(value);
            },
            getObject: function(key) {
                return JSON.parse($window.localStorage[key] || '{}');
            }
        }
    }
])
.factory("Pathfinder", ["$http", "$q", "Utilities",
    function($http, $q, Utilities) {
        return {
            generateTerrain: function(cols, rows, minValue, maxValue) {
                var deferred = $q.defer();

                $http({
                    method: "GET",
                    url: "api/pathfinder/generate_terrain",
                    params: {
                        "cols": cols,
                        "rows": rows,
                        "min": minValue,
                        "max": maxValue,
                        "nonce": Utilities.randomString()
                    }
                }).then(
                    function(response) {
                        deferred.resolve(response.data);
                    },
                    function(reason) {
                        deferred.reject(reason);
                    }
                );

                return deferred.promise;
            },
            findPath: function(grid, origin, destination, moveset) {
                var deferred = $q.defer();

                $http({
                    method: "POST",
                    url: "api/pathfinder/find_path",
                    data: {
                        "grid": grid,
                        "origin": origin,
                        "destination": destination,
                        "moveset": moveset
                    }
                }).then(
                    function(response) {
                        deferred.resolve(response.data);
                    },
                    function(reason) {
                        deferred.reject(reason);
                    }
                );

                return deferred.promise;
            }
        }
    }
])

.factory("Flickr", ["$http", "$q", "Utilities",
    function($http, $q, Utilities) {
        return {
            api: "https://api.flickr.com/services/feeds/photos_public.gne",
            currentTag: undefined,
            seq: 1,
            callback: function(response) {
                var n = response.items.length;
                var data = [];
                for (var i = 0; i < n; i++) {
                    // Check title
                    var title = response.items[i].title.trim();
                    if (title == "" || title == null || title == undefined) {
                        response.items[i].title = "Untitled";
                    }

                    // extract author info
                    var author = response.items[i].author;
                    if (author) {
                        response.items[i].author = author.substring(19, author.length - 2);
                    }
                    data.push({
                        seq: this.seq,
                        title: response.items[i].title,
                        author: response.items[i].author,
                        photoUrl: response.items[i].media.m,
                        link: response.items[i].link,
                        tags: response.items[i].tags
                    });
                    this.seq++;
                }

                return data;
            },
            getNextPhotoSeq: function() {
                var nextSeq = this.seq;
                this.seq++;
                return nextSeq;
            },
            getPhotos: function(tags) {
                var apiUrl = "https://api.flickr.com/services/feeds/photos_public.gne";
                var params = {
                    "format": "json"
                };

                if (tags) {
                    this.currentTag = tags;
                } else {
                    this.currentTag = undefined;
                }

                params["tags"] = this.currentTag;

                $http.jsonp(apiUrl, { params: params });

                return true;
            },
            likePhoto: function(user, photo) {
                var deferred = $q.defer();

                $http({
                    method: "POST",
                    url: "api/photo/like",
                    data: {
                        "user": user,
                        "photo": photo
                    }
                }).then(
                    function(response) {
                        deferred.resolve(response.data);
                    },
                    function(reason) {
                        deferred.reject(reason);
                    }
                );

                return deferred.promise;
            },
            getLikedPhotos: function(user) {
                var deferred = $q.defer();

                $http({
                    method: "GET",
                    url: "api/photo/liked_photos",
                    params: {
                        "user": user,
                        "nonce": Utilities.randomString()
                    }
                }).then(
                    function(response) {
                        deferred.resolve(response);
                    },
                    function(reason) {
                        deferred.reject(reason);
                    }
                );

                return deferred.promise;
            }
        }
    }
]);
