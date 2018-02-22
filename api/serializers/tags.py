""" . """
from rest_framework import serializers
from tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag
