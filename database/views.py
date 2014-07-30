from django.shortcuts import render_to_response
from django.template import RequestContext, add_to_builtins
from django.db.models import Q

from django_datatables_view.base_datatable_view import BaseDatatableView

from database.models import Summary

def top10(request):
    return render_to_response('top10.html', {}, RequestContext(request))
    
def samples(request):
    return render_to_response('samples.html', {}, RequestContext(request))
    
class SummaryDatatablesView(BaseDatatableView):
    model = Summary
    columns = [
        'sampletag',
        #'ispublished',
        'grade',
        'sequencingcenter',
        'strain',
        'quality',
        'coverage',
        'meanlength',
        'sequencetype', 
        'clonalcomplex',
        #'coveragetype',
        #'primertype',
        #'proteintype',
        'n50', 
        'mincontig',
        'mean',
    ]
    order_columns = [
        'sampletag',
        #'ispublished',
        'grade',
        'sequencingcenter',
        'strain',
        'quality',
        'coverage',
        'meanlength',
        'sequencetype', 
        'clonalcomplex',
        #'coveragetype',
        #'primertype',
        #'proteintype',
        'n50', 
        'mincontig',
        'mean',
    ]
    

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'grade':
            if row.meanlength >= 75:
                if row.coverage >= 45 and row.quality >= 30:
                    return 'Gold'
                elif row.coverage >= 20 and row.quality >= 20:
                    return 'Silver'
                else:
                    return 'Bronze'
            else:
                return 'Bronze'
        else:
            return super(SummaryDatatablesView, self).render_column(row, column)
  
    
    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(
                    Q(sampletag__icontains=sSearch) |
                    Q(sequencingcenter__icontains=sSearch) |
                    Q(strain__icontains=sSearch) | 
                    Q(quality__icontains=sSearch) |
                    Q(coverage__icontains=sSearch) | 
                    Q(meanlength__icontains=sSearch) |
                    Q(sequencetype__icontains=sSearch) | 
                    Q(clonalcomplex__icontains=sSearch) |
                    Q(n50__icontains=sSearch) |
                    Q(mincontig__icontains=sSearch) | 
                    Q(mean__icontains=sSearch)
                )
            
        return qs