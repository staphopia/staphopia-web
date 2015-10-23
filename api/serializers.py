""" . """
from rest_framework import serializers
from sample.models import MetaData


class SampleSerializer(serializers.HyperlinkedModelSerializer):
    metadata = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    kmers = serializers.SerializerMethodField()
    genes = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        url = self.context['request'].build_absolute_uri()
        return '{0}{1}/metadata/'.format(url, obj.sample_tag)

    def get_linking_url(self, obj, link):
        url = self.context['request'].build_absolute_uri()
        url = url.replace('samples', link)
        return '{0}{1}/'.format(url, obj.sample_tag)

    def get_variants(self, obj):
        return self.get_linking_url(obj, 'variants')

    def get_kmers(self, obj):
        return self.get_linking_url(obj, 'kmers')

    def get_genes(self, obj):
        return self.get_linking_url(obj, 'genes')

    class Meta:
        model = MetaData
        fields = ('metadata', 'variants', 'kmers', 'genes', 'id', 'sample_tag')


class MetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaData
