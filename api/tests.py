from collections import OrderedDict
import json

from django.contrib.auth.models import User

from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.test import APIClient

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.tags import get_samples_by_tag

from sample.models import Sample
TEST_TAG = 'public-5'


class TestsViewSet(CustomReadOnlyModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    throttle_classes = ()
    client = APIClient()
    user = User.objects.get(username='ena')
    queryset = ''

    def __init__(self, *args, **kwargs):
        super(TestsViewSet, self).__init__(*args, **kwargs)
        self.client.force_authenticate(user=self.user)
        self.samples = [s['sample_id']
                        for s in get_samples_by_tag(TEST_TAG, is_id=False)]
        self.endpoints = [
            'Connection Related',
            'test_status',
            # Single Sample
            'Single Sample Related',
            'test_sample',
            'test_quality',
            'test_assembly',
            'test_contig',
            'test_gene',
            'test_indel',
            'test_snp',
            'test_mlst',
            'test_sccmec_primer',
            'test_sccmec_primer_predict',
            'test_sccmec_subtype',
            'test_sccmec_subtype_predict',
            # Multiple Samples
            'Multiple Sample Related',
            'test_samples',
            'test_qualities',
            'test_assemblies',
            'test_indels',
            'test_snps',
            'test_mlsts',
            'test_sccmec_primers',
            'test_sccmec_primers_predict',
            'test_sccmec_subtypes',
            'test_sccmec_subtypes_predict',
        ]

    def __get(self, url):
        response = self.client.get(url)
        return [json.loads(response.content), response.status_code]

    def __post(self, url, ids):
        response = self.client.post(url, {'ids': ids}, format='json')
        return [json.loads(response.content), response.status_code]

    def list(self, request):
        """
        Stored metadata information for a given sample.
        """
        base_url = request.build_absolute_uri()
        urls = OrderedDict()
        for endpoint in self.endpoints:
            if endpoint.endswith('Related'):
                urls[endpoint] = ''
            else:
                urls[endpoint] = '{0}{1}/'.format(base_url, endpoint)

        return Response(urls)

    @list_route(methods=['get'])
    def test_status(self, request):
        response = self.client.get('/api/status/')
        return Response(json.loads(response.content),
                        status=response.status_code)

    @list_route(methods=['get'])
    def test_samples(self, request):
        data, status = self.__get(f'/api/sample/?tag={TEST_TAG}')
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sample(self, request):
        sample = self.samples[0]
        data, status = self.__get(f'/api/sample/{sample}/')
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_quality(self, request):
        url = '/api/sample/{0}/qc/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_qualities(self, request):
        url = '/api/sequence-quality/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_assembly(self, request):
        url = '/api/sample/{0}/assembly/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_assemblies(self, request):
        url = '/api/assembly/stat/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_contig(self, request):
        url = '/api/sample/{0}/contigs/?contig=30'.format(
            self.samples[0]
        )
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_gene(self, request):
        url = '/api/sample/{0}/genes/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status,
                                       limit=1)

    @list_route(methods=['get'])
    def test_indel(self, request):
        url = '/api/sample/{0}/indels/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status,
                                       limit=10)

    @list_route(methods=['get'])
    def test_indels(self, request):
        url = '/api/variant/indel/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status,
                                       limit=10)

    @list_route(methods=['get'])
    def test_snp(self, request):
        url = '/api/sample/{0}/snps/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status,
                                       limit=10)

    @list_route(methods=['get'])
    def test_snps(self, request):
        url = '/api/variant/snp/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status,
                                       limit=10)

    @list_route(methods=['get'])
    def test_mlst_srst2(self, request):
        url = '/api/sample/{0}/st_srst2/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_mlst_srst2_bulk(self, request):
        url = '/api/mlst/srst2/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_mlst(self, request):
        url = '/api/sample/{0}/st/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_mlsts(self, request):
        url = '/api/mlst/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_primer(self, request):
        url = '/api/sample/{0}/sccmec_primers/'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_primer_predict(self, request):
        url = '/api/sample/{0}/sccmec_primers/?predict'.format(self.samples[0])
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_primers(self, request):
        url = '/api/sccmec/primer/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_primers_predict(self, request):
        url = '/api/sccmec/primer/bulk_by_sample/?predict'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_subtype(self, request):
        url = '/api/sample/{0}/sccmec_subtypes/'.format(
            self.samples[0]
        )
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_subtype_predict(self, request):
        url = '/api/sample/{0}/sccmec_subtypes/?predict'.format(
            self.samples[0]
        )
        data, status = self.__get(url)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_subtypes(self, request):
        url = '/api/sccmec/subtype/bulk_by_sample/'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)

    @list_route(methods=['get'])
    def test_sccmec_subtypes_predict(self, request):
        url = '/api/sccmec/subtype/bulk_by_sample/?predict'
        data, status = self.__post(url, self.samples)
        return self.formatted_response(data['results'], status=status)
