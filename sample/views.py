from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
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
        sample_list = Sample.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(sample_list, 20)
        try:
            samples = paginator.page(page)
        except PageNotAnInteger:
            samples = paginator.page(1)
        except EmptyPage:
            samples = paginator.page(paginator.num_pages)

        # Fix displaying all pages
        # Edited from Blackeagle52's response on StackOverflow
        # http://stackoverflow.com/questions/30864011/display-only-some-of-the-page-numbers-by-django-pagination
        index = samples.number - 1
        max_index = len(paginator.page_range)
        total = 11
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 6 if index <= max_index - 6 else max_index

        if end_index - start_index != total:
            if end_index == max_index:
                start_index = max_index - total
            else:
                end_index = total

        # My new page range
        page_range = list(paginator.page_range)[start_index:end_index]

        return render(request, 'samples.html',
                      {'samples': samples,
                       'page_range': page_range,
                       'total_pages': max_index})


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
