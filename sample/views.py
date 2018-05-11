from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.db import transaction

from sample.datatable import DataTable
from sample.forms import SampleSubmissionForm
from sample.models import Sample

from api.utils import query_database


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
        return render(request, 'submission.html', context={'form': form})
    else:
        return HttpResponseRedirect('/')


def top10(request):
    return render(request, 'top10.html')


def sample(request, sample_id=None):
    if sample_id:
        row = query_database(
            """
            SELECT count(id)
            FROM sample_sample
            WHERE id={0} USER_PERMISSION;""".format(sample_id))[0]

        return render(request, 'sample/results.html',
                      context={'sample_id': sample_id,
                               'sample_results': True,
                               'viewable': int(row['count'])})
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
                      context={'samples': samples, 'page_range': page_range,
                               'total_pages': max_index})


def sample_summary(request):
    # Filter the based on query
    if 'order[0][column]' in request.GET:
        # Columns to include in table
        cols = [
            'sample_id', 'name', 'rank', 'is_published', 'st', 'sample_accession',
            'strain', 'collection_date', 'location', 'isolation_source'
        ]

        # Initialize a DataTable
        dt = DataTable(cols)
        order_by = cols[int(request.GET['order[0][column]'])]
        direction = request.GET['order[0][dir]']
        query = request.GET['search[value]'].lower().strip(' ')
        dt.filter_table(query, order_by, direction, limit=request.GET['length'],
                        offset=request.GET['start'])

        # Return JSON output
        return HttpResponse(dt.get_json_response())
    else:
        return redirect('/sample/')
