from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest import views

urlpatterns = format_suffix_patterns(patterns('',
    url(r'^users/(?P<username>\w+)/?$', views.UserDetail.as_view(),
        name='user-detail'),
    url(r'^users/(?P<username>\w+)/following/?$', views.FollowingList.as_view(),
        name='user-following'),
    url(r'^users/(?P<username>\w+)/followers/?$', views.FollowersList.as_view(),
        name='user-followers'),
    url(r'^users/(?P<username>\w+)/follow/?$', views.FollowDetail.as_view(),
        name='user-follow'),
    url(r'^users/(?P<username>\w+)/photos/?$', views.PublicationList.as_view(),
        name='publication-list'),
    url(r'^photos/(?P<pk>[0-9]+)/?$', views.PublicationDetail.as_view(),
        name='publication-detail'),
    url(r'^photos/(?P<pk>[0-9]+)/comments/?$', views.CommentList.as_view(),
        name='comment-list'),
    url(r'^comments/(?P<pk>[0-9]+)/?$', views.CommentDetail.as_view(),
        name='comment-detail'),
    url(r'^feed/?$', views.FeedList.as_view(),
        name='feed'),
    url(r'^search/?$', views.SearchList.as_view(),
        name='search'),
))