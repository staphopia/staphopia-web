from rest_framework import routers

from api.viewsets.assemblies import AssemblyViewSet, ContigViewSet
from api.viewsets.enas import (
    EnaStudyViewSet,
    EnaExperimentViewSet,
    EnaRunViewSet
)

from api.viewsets.annotations import (
    AnnotationViewSet,
    AnnotationRepeatViewSet,
    AnnotationFeatureViewSet,
    AnnotationInferenceViewSet,
)

from api.viewsets.kmers import KmerViewSet

from api.viewsets.samples import SampleViewSet, MetadataViewSet
from api.viewsets.tags import TagViewSet

from api.viewsets.resistances import ResistanceAribaViewSet

from api.viewsets.sccmecs import (
    SCCmecCassetteViewSet,
    SCCmecCoverageViewSet,
    SCCmecPrimerViewSet,
    SCCmecProteinViewSet,
    SCCmecSubtypeViewSet
)

from api.viewsets.search import SearchViewSet
from api.viewsets.sequences import SequenceStatViewSet
from api.viewsets.sequence_types import MLSTViewSet

from api.viewsets.top import TopViewSet
from api.viewsets.info import InfoViewSet, StatusViewSet

from api.viewsets.variants import (
    SNPViewSet,
    InDelViewSet,
    VariantAnnotationViewSet,
    CommentViewSet,
    FeatureViewSet,
    FilterViewSet,
    ReferenceViewSet,
    VariantViewSet
)

# Test Related
from api.tests import TestsViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

# Sample Related Tables
router.register(r'sample', SampleViewSet)
router.register(r'tag', TagViewSet)
# router.register(r'publication', PublicationViewSet)
# router.register(r'resistance', ResistanceViewSet)
router.register(r'metadata', MetadataViewSet, base_name='metadata')

# Assembly related table
router.register(r'assembly/stat', AssemblyViewSet)
router.register(r'assembly/contig', ContigViewSet)

# ENA Related Tables
router.register(r'ena/study', EnaStudyViewSet)
router.register(r'ena/experiment', EnaExperimentViewSet,
                base_name='experiment')
router.register(r'ena/run', EnaRunViewSet)

# Gene annotation related tables
router.register(r'annotation/gene', AnnotationViewSet)
router.register(r'annotation/feature', AnnotationFeatureViewSet)
router.register(r'annotation/repeat', AnnotationRepeatViewSet)
router.register(r'annotation/inference', AnnotationInferenceViewSet)

# Information related views
router.register(r'info', InfoViewSet, base_name='info')
router.register(r'top', TopViewSet, base_name='top')

# Kmer related tables
router.register(r'kmer', KmerViewSet)

# Seqeunce Type (MLST) Related Tables
router.register(r'mlst', MLSTViewSet)

# Resistance Related Tables
router.register(r'resistance/ariba', ResistanceAribaViewSet,
                base_name='resistance_ariba')

# SCCmec related tables
router.register(r'sccmec/cassette', SCCmecCassetteViewSet)
router.register(r'sccmec/coverage', SCCmecCoverageViewSet)
router.register(r'sccmec/primer', SCCmecPrimerViewSet, base_name='primer')
router.register(r'sccmec/protein', SCCmecProteinViewSet)
router.register(r'sccmec/subtype', SCCmecSubtypeViewSet, base_name='subtype')

# Seqeunce quality related table
router.register(r'sequence-quality', SequenceStatViewSet)

router.register(r'status', StatusViewSet, base_name='status')

# Variant Related Tables
router.register(r'variant/snp', SNPViewSet)
router.register(r'variant/indel', InDelViewSet)
router.register(r'variant/annotation', VariantAnnotationViewSet)
router.register(r'variant/comment', CommentViewSet)
router.register(r'variant/feature', FeatureViewSet)
router.register(r'variant/filter', FilterViewSet)
router.register(r'variant/reference', ReferenceViewSet)
router.register(r'variant', VariantViewSet)

# Test Related Tables
router.register(r'tests', TestsViewSet, base_name='tests')
router.register(r'search', SearchViewSet, base_name='search')
