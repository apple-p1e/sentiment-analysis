from rest_framework import serializers
from django.contrib.auth.models import User
from website.models import Publication, Comment, Follower


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    polarity = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ('id', 'username', 'text', 'created', 'polarity')


class PublicationSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    comments_count = serializers.ReadOnlyField(source='comments.count')
    image_url = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        view = self.context['view']
        return view.request.build_absolute_uri(obj.image_file.url)
        #return "http://127.0.0.1:8000" + obj.image_file.url

    def get_thumb_url(self, obj):
        view = self.context['view']
        return view.request.build_absolute_uri(obj.image_file.thumb_url)

    class Meta:
        model = Publication
        fields = ('id', 'image_url', 'thumb_url', 'username', 'created',
                  'comments_count')


class UserSerializer(serializers.ModelSerializer):
    following_count = serializers.ReadOnlyField(source='following.count')
    followers_count = serializers.ReadOnlyField(source='followers.count')
    publications_count = serializers.ReadOnlyField(source='publications.count')

    class Meta:
        model = User
        fields = ('id', 'username', 'following_count', 'followers_count',
                  'publications_count')


class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='following.username')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        view = self.context['view']
        user = view.request.user
        following = User.objects.get(username=obj.following.username)
        if user.username == following.username:
            return None
        if not Follower.objects.filter(user=user, following=following):
            return False
        return True

    class Meta:
        model = Follower
        fields = ('username', 'status')


class FollowersSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        view = self.context['view']
        user = view.request.user
        follower = User.objects.get(username=obj.user.username)
        if user.pk == follower.pk:
            return None
        if not Follower.objects.filter(user=user, following=follower):
            return False
        return True

    class Meta:
        model = Follower
        fields = ('username', 'status')


class SearchUserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        view = self.context['view']
        user = view.request.user
        if user.pk == obj.pk:
            return None
        if not Follower.objects.filter(user=user, following=obj):
            return False
        return True

    class Meta:
        model = User
        fields = ('username', 'status')