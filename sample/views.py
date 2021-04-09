from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.db import transaction

from sample.models import Sample


def top10(request):
    return render(request, 'top10.html')
