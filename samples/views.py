from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import transaction

from samples.forms import SampleSubmissionForm
from samples.models import Sample


@transaction.commit_on_success
def submission(request):
    if request.user.is_authenticated:
        form = None
        save_results = None
        if request.method == 'POST':
            num_samples = Sample.objects.filter(user_id=request.user.id).count()
            sample_tag = '{0}_{1}'.format(request.user.username,
                                          str(num_samples+1).zfill(6))
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
