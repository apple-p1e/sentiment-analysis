from django.conf.urls import patterns, url

urlpatterns = patterns('website.views',
    url(r'^/?$', 'home', name='home'),
    url(r'^login/$', 'login_user', name='login'),
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^feed/$', 'feed', name='feed'),
    url(r'^users/(?P<username>\w+)/$', 'profile', name='profile'),
    url(r'^p/(?P<pk>[0-9]+)/$', 'publication', name='publication'),
    url(r'^upload/$', 'upload', name='upload'),
    url(r'^classification/$', 'classification', name='classification'),
)