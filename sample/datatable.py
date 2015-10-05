import json
from cStringIO import StringIO

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

from staphopia.utils import REMatcher


class DataTable(object):

    def __init__(self, model, cols, searchable):
        self.objects = model.objects.all()
        self.total_records = self.objects.count()
        self.filtered_records = self.objects.count()
        self.cols = cols
        self.searchable = searchable

    def filter_table(self, query):
        self.query = query
        self.__parse_query()
        self.__filter_text()
        self.__filter_patterns()
        self.filtered_records = self.objects.count()

    def __parse_query(self):
        self.query_text = []
        self.patterns = []
        for q in self.query.split():
            if '=' in q:
                self.patterns.append(q)
            else:
                self.query_text.append(q)

    def __filter_text(self):
        # Filter out Text searches
        queries = []
        for q in self.query_text:
            if q.startswith('!'):
                for f in self.searchable:
                    queries.append(~Q(**{f + '__icontains': q}))
            else:
                queries += [
                    Q(**{f + '__icontains': q}) for f in self.searchable
                ]

        if queries:
            qs = reduce(lambda x, y: x | y, queries)
            self.objects = self.objects.filter(qs)

    def __filter_patterns(self):
        # Filter out regex patterns
        queries = []
        for q in self.patterns:
            m = REMatcher(q)

            if m.match(r"^st=(?P<st>\d+)$"):
                queries.append(Q(**{'st_stripped__exact': m.group('st')}))
            elif m.match(r"^!st=(?P<st>\d+)$"):
                queries.append(~Q(**{'st_stripped__exact': m.group('st')}))

        if queries:
            qs = reduce(lambda x, y: x | y, queries)
            self.objects = self.objects.filter(qs)

    def sort_table(self, order_by, column):
        order = dict(enumerate(self.cols))
        direction = {'asc': '', 'desc': '-'}
        ordering = (
            direction[order_by] +
            order[column]
        )
        self.objects = self.objects.order_by(ordering)

    def produce_json(self, start, length):
        self.objects = self.objects[start: (start + length)]
        data = [
            map(lambda field: getattr(obj, field), self.cols)
            for obj in self.objects
        ]

        # define response
        self.json_response = {
            'data': data,
            'recordsTotal': self.total_records,
            'recordsFiltered': self.filtered_records,
        }

    def get_json_response(self):
        # serialize to json
        s = StringIO()
        json.dump(self.json_response, s, cls=DjangoJSONEncoder)
        s.seek(0)
        return s.read()
