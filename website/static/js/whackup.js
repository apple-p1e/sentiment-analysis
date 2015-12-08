( function() {
    var app = angular.module('whackup', []);

    app.config(['$httpProvider', '$interpolateProvider',
        function($httpProvider, $interpolateProvider) {
            /* for compatibility with django template engine */
            $interpolateProvider.startSymbol('{$');
            $interpolateProvider.endSymbol('$}');
            /* csrf */
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    }]);

    app.controller('FeedController', ['$http', function($http){
        var feed = this;
        feed.publications = [];
        $http.get('/api/feed').success(function(data){
            feed.publications = data;
        });
    }]);

    app.controller('ProfileController', ['$http', function($http){
        var ctrl = this;
        ctrl.status = "";
        ctrl.publications = [];
        ctrl.followButton = "";
        ctrl.following_count = 0;
        ctrl.followers_count = 0;
        ctrl.publications_count = 0;
        ctrl.init = function(username, profile, followers, following, publications){
            ctrl.followers_count = followers;
            ctrl.following_count = following;
            ctrl.publications_count = publications;
            if (username==profile) {
                ctrl.status = "It's you"
            } else {
                $http.get('/api/users/'+profile+'/follow')
                    .success(function(data){
                        if (data.detail) {
                            ctrl.status = "Unfollow";
                        } else {
                            ctrl.status = "Follow";
                        }
                });
                ctrl.followButton = function(){
                    $http.post('/api/users/'+profile+'/follow')
                        .success(function(data){
                            if (ctrl.status == "Follow") {
                                ctrl.status = "Unfollow";
                                ctrl.followers_count += 1;
                            } else {
                                ctrl.status = "Follow";
                                ctrl.followers_count -= 1;
                            }
                    });
                }
            }
            $http.get('/api/users/'+profile+'/photos')
                .success(function(data){
                    ctrl.publications = data;
                })
        };

    }]);

    app.controller('SignupController', ['$http', function($http){
        var ctrl = this;
        ctrl.data = {};
        ctrl.submit = function(){
            $http.post('/api/users', {
                username: ctrl.data.username,
                email: ctrl.data.email,
                password: ctrl.data.password
            })
                .success(function(data, status) {})
        };
    }]);

    app.controller('PublicationController', ['$http', '$window', function($http, $window){
        var ctrl = this;
        var user = null;
        var p_id = null;
        ctrl.comments = [];
        ctrl.comment = "";
        var updateComments = function(){
            $http.get('/api/photos/'+p_id+'/comments')
                .success(function(data){
                    ctrl.comments = data;
                });
            ctrl.comment = "";
        };
        ctrl.init = function(username, pk){
            user = username;
            p_id = pk;
            updateComments();
        };
        ctrl.submit = function(){
            $http.post('/api/photos/'+p_id+'/comments', {
                text: ctrl.comment
            })
                .success(function(data, status){
                    updateComments();
                });
        };
        ctrl.deletePublication = function(){
            $http.delete('/api/photos/'+p_id)
                .success(function(data, status) {
                    $window.location = "/users/"+user;
                });
        };
        ctrl.deleteComment = function(pk){
            $http.delete('/api/comments/'+pk)
                .success(function(data, status){
                    updateComments();
                })
        };
        ctrl.show = function(owner){
            return user == owner;
        };
        ctrl.isNegative = function(polarity){
            return polarity === 1;
        };
        ctrl.isPositive = function(polarity){
            return polarity === 2;
        };
    }]);

    $(document).ready(function(){
        $("#header").on("click", ".toggle-sidebar",
        function(){
            $("#sidebar").slideToggle(0);
        });
        $(".upload").on("click", $(this),
        function(){
            $(".menu").slideToggle(0);
            $(".upload-form").slideToggle(0);
        });
        $(".upload-form").on("click", "input[type=button]",
        function(){
            $(".upload-form").slideToggle(0);
            $(".menu").slideToggle(0);
        });
    });

})();

var getName = function (str){
    if (str.lastIndexOf('\\')){
        var i = str.lastIndexOf('\\')+1;
    }
    else{
        var i = str.lastIndexOf('/')+1;
    }
    var filename = str.slice(i);
    var uploaded = $(".label");
    uploaded.text(filename);
};