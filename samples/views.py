from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import transaction

from django_datatables_view.base_datatable_view import BaseDatatableView

from samples.forms import SampleSubmissionForm
from samples.models import Sample, SamplesSummary


@transaction.atomic
def submission(request):
    if request.user.is_authenticated:
        form = None
        save_results = None
        if request.method == 'POST':
            num_samples = Sample.objects.filter(user_id=request.user.id).count()
            sample_tag = '{0}_{1}'.format(request.user.username,
                                          str(num_samples + 1).zfill(6))
            form = SampleSubmissionForm(request.user.id, request.POST,
                                        request.FILES,
                                        instance=Sample(user=request.user,
                                                        sample_tag=sample_tag))
            if form.is_valid():
                new_sample = form.save()
                save_upload = form.save_upload(new_sample.pk, request.FILES)
                return HttpResponseRedirect('/')
        else:
            form = SampleSubmissionForm(request.user.id)
        return render_to_response('submission.html',
                                  {'form': form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')


def top10(request):
    return render_to_response('top10.html', {}, RequestContext(request))


def samples(request, sample_tag=None):
    if sample_tag:
        return render_to_response('sample/results.html',
                                  {'sample_tag': sample_tag},
                                  RequestContext(request))
    else:
        return render_to_response('samples.html', {}, RequestContext(request))


class SummaryDatatablesView(BaseDatatableView):
    model = SamplesSummary
    columns = [
        'sample_tag',
    ]
    order_columns = [
        'sample_tag',
    ]
