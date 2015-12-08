from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest.permissions import IsOwnerOrReadOnly
from rest import serializers
from website.models import Publication, Follower, Comment


class PublicationDetail(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (SessionAuthentication,)
    serializer_class = serializers.Publication
    queryset = Publication.objects.all()


class PublicationList(generics.ListAPIView):
    serializer_class = serializers.PublicationSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        offset = self.request.GET.get('offset', 0)
        limit = self.request.GET.get('limit', 0)
        try:
            offset = int(offset)
        except ValueError:
            offset = 0
        try:
            limit = int(limit)
        except ValueError:
            limit = 0
        if not limit:
            sum_ = None
        else:
            sum_ = offset + limit
        username = self.kwargs['username']
        publications = Publication.objects.filter(
            user__username=username).order_by('-created')
        return publications[offset:sum_]


class CommentList(generics.ListCreateAPIView):
    serializer_class = serializers.CommentSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Comment.objects.filter(publication__pk=pk)

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        p = Publication.objects.get(pk=pk)
        serializer.save(user=self.request.user, publication=p)


class CommentDetail(generics.DestroyAPIView):
    serializer_class = serializers.CommentSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Comment.objects.all()


class UserDetail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'


class FollowersList(generics.ListAPIView):
    serializer_class = serializers.FollowersSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        username = self.kwargs['username']
        return Follower.objects.filter(following__username=username)


class FollowingList(generics.ListAPIView):
    serializer_class = serializers.FollowingSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        username = self.kwargs['username']
        return Follower.objects.filter(user__username=username)


class FollowDetail(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request, username):
        following = User.objects.filter(username=username)
        if not following:
            content = {"detail": "Not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
            following = following[0]
        user = request.user
        if user == following:
            content = {"detail": "You can not follow yourself."}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        if not Follower.objects.filter(user=user, following=following):
            follower = Follower(user=user, following=following)
            follower.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            follower = Follower.objects.get(following=following, user=user)
            follower.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, username):
        following = User.objects.filter(username=username)
        if not following:
            content = {"detail": "Not found."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
            following = following[0]
        user = request.user
        if user == following:
            content = {"detail": "You can not follow yourself."}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        if not Follower.objects.filter(user=user, following=following):
            content = {"detail": False}
        else:
            content = {"detail": True}
        return Response(content, status=status.HTTP_200_OK)


class FeedList(generics.ListAPIView):
    serializer_class = serializers.PublicationSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )

    def get_queryset(self):
        user = self.request.user
        publications = []
        publications.extend(Publication.objects.filter(user=user))
        for follower in Follower.objects.filter(user=user):
            publications.extend(follower.following.publications.all())
        publications.sort(key=lambda obj: obj.created)
        publications.reverse()
        return publications


class SearchList(generics.ListAPIView):
    serializer_class = serializers.SearchUserSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get_queryset(self):
        query = self.request.GET.get('q')
        return User.objects.filter(username=query)