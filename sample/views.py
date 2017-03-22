from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import transaction

from sample.datatable import DataTable
from sample.forms import SampleSubmissionForm
from sample.models import Sample, SampleSummary


@transaction.atomic
def submission(request):
    if request.user.is_authenticated:
        form = None
        if request.method == 'POST':
            num_samples = Sample.objects.filter(
                user_id=request.user.id
            ).count()
            sample_tag = '{0}_{1}'.format(request.user.username,
                                          str(num_samples + 1).zfill(6))
            form = SampleSubmissionForm(
                request.user.id, request.POST,
                request.FILES,
                instance=Sample(user=request.user, sample_tag=sample_tag)
            )
            if form.is_valid():
                new_sample = form.save()
                form.save_upload(new_sample.pk, request.FILES)
                return HttpResponseRedirect('/')
        else:
            form = SampleSubmissionForm(request.user.id)
        return render_to_response('submission.html',
                                  {'form': form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')


def top10(request):
    return render_to_response('top10.html', {}, RequestContext(request))


def sample(request, sample_id=None):
    if sample_id:
        return render_to_response('sample/results.html',
                                  {'sample_id': sample_id},
                                  RequestContext(request))
    else:
        return render_to_response('samples.html', {}, RequestContext(request))


def sample_summary(request):

    # Columns to include in table
    cols = [
        'sample_tag', 'rank', 'sequencing_center', 'st_stripped', 'q_score',
        'coverage', 'mean_read_length'
    ]

    # Columns to search text against
    searchable = [
        'sample_tag', 'username', 'sequencing_center'
    ]

    # Initialize a DataTable
    dt = DataTable(SampleSummary, cols, searchable)

    # Filter the based on query
    query = request.GET['search[value]'].lower()
    if query:
        dt.filter_table(query)

    # Sort the table
    dt.sort_table(
        request.GET['order[0][dir]'],
        int(request.GET['order[0][column]'])
    )

    # Produce JSON
    dt.produce_json(
        int(request.GET['start']),
        int(request.GET['length'])
    )

    # Return JSON output
    return HttpResponse(dt.get_json_response())
