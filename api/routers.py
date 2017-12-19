from rest_framework import routers

from api.viewsets.assemblies import AssemblyViewSet, ContigViewSet
from api.viewsets.enas import (
    EnaStudyViewSet,
    EnaExperimentViewSet,
    EnaRunViewSet
)

from api.viewsets.genes import (
    GeneClusterViewSet,
    GeneFeatureViewSet,
    GeneProductViewSet,
    GeneInferenceViewSet,
    GeneNoteViewSet,
    GeneBlastViewSet
)

from api.viewsets.kmers import KmerViewSet

from api.viewsets.samples import (
#    PublicationViewSet,
    SampleViewSet,
#    TagViewSet,
#    ResistanceViewSet,
#    MetaDataViewSet
)

from api.viewsets.sccmecs import (
    SCCmecCassetteViewSet,
    SCCmecCoverageViewSet,
    SCCmecPrimerViewSet,
    SCCmecProteinViewSet,
    SCCmecSubtypeViewSet
)

from api.viewsets.search import SearchViewSet
from api.viewsets.sequences import SequenceStatViewSet
# from api.viewsets.sequence_types import MlstBlastViewSet

from api.viewsets.top import TopViewSet
from api.viewsets.info import InfoViewSet, StatusViewSet

from api.viewsets.variants import (
    SNPViewSet,
    InDelViewSet,
    AnnotationViewSet,
    CommentViewSet,
    FeatureViewSet,
    FilterViewSet,
    ReferenceViewSet
)

# Test Related
from api.tests import TestsViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

# Sample Related Tables
router.register(r'sample', SampleViewSet)
# router.register(r'tag', TagViewSet)
# router.register(r'publication', PublicationViewSet)
# router.register(r'resistance', ResistanceViewSet)
# router.register(r'metadata', MetaDataViewSet, base_name='metadata')

# Assembly related table
router.register(r'assembly/stat', AssemblyViewSet)
router.register(r'assembly/contig', ContigViewSet)

# ENA Related Tables
router.register(r'ena/study', EnaStudyViewSet)
router.register(r'ena/experiment', EnaExperimentViewSet,
                base_name='experiment')
router.register(r'ena/run', EnaRunViewSet)

# Gene annotation related tables
router.register(r'gene/cluster', GeneClusterViewSet)
router.register(r'gene/feature', GeneFeatureViewSet)
router.register(r'gene/product', GeneProductViewSet)
router.register(r'gene/inference', GeneInferenceViewSet)
router.register(r'gene/note', GeneNoteViewSet)
router.register(r'gene/blast', GeneBlastViewSet)

# Information related views
router.register(r'info', InfoViewSet, base_name='info')
router.register(r'top', TopViewSet, base_name='top')

# Kmer related tables
router.register(r'kmer', KmerViewSet)

# Seqeunce Type (MLST) Related Tables
# router.register(r'mlst/blast', MlstBlastViewSet)

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
router.register(r'variant/annotation', AnnotationViewSet)
router.register(r'variant/comment', CommentViewSet)
router.register(r'variant/feature', FeatureViewSet)
router.register(r'variant/filter', FilterViewSet)
router.register(r'variant/reference', ReferenceViewSet)

# Test Related Tables
router.register(r'tests', TestsViewSet, base_name='tests')
router.register(r'search', SearchViewSet, base_name='search')
