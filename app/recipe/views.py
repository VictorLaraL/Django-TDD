"""
Views for the recipe APIs.
"""
from rest_framework import (
    viewsets,
    mixins
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient,
    )


class RecipeViewSet(viewsets.ModelViewSet):
    """ Viewsets for recipe APIs. """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Retrive recipes for authenticated user. """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self,):
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe. """
        serializer.save(user=self.request.user)


class TagViewSet(
                viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin
                ):
    """ Viewsets for tag API's """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter  querysets to authenticated user. """
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(
                        viewsets.GenericViewSet,
                        mixins.ListModelMixin
                        ):
    """ Viewsets for ingredients """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter querysets to authenticated user. """
        return self.queryset.filter(user=self.request.user).order_by('-name')
