from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import website.urls
import rest.urls

urlpatterns = [
    # Examples:
    # url(r'^$', 'whackup.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(website.urls)),
    url(r'^api/', include(rest.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
