""" . """
from rest_framework import serializers
from django.contrib.auth.models import User
from samples.models import Sample
from analysis.models import (
    Variant,
    VariantToSNP
)

class SampleSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_https_url')

    def get_https_url(self, obj):
        url = self.context['request'].build_absolute_uri()
        url = url.replace('http', 'https')
        return '{0}{1}/'.format(url, obj.id)

    class Meta:
        model = Sample
        fields = ('url', 'id', 'sample_tag')

class VariantSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_https_url')

    def get_https_url(self, obj):
        url = self.context['request'].build_absolute_uri()
        url = url.replace('http', 'https')
        sample_tag = obj.sample.sample_tag
        return '{0}{1}/'.format(url, sample_tag)

    class Meta:
        model = Variant
        fields = ('url', 'sample_tag')
