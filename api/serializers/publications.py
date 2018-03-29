""" . """
from rest_framework import serializers
from publication.models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Publication
