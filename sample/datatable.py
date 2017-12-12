import json
from io import StringIO

from django.core.serializers.json import DjangoJSONEncoder

from search.models import History

from api.queries.search import basic_search, total_samples, get_filtered_count


class DataTable(object):

    def __init__(self, cols):
        self.objects = None
        self.total_records = total_samples()
        self.filtered_records = self.total_records
        self.cols = cols

    def filter_table(self, query, order_by, direction, limit="", offset=""):
        if query:
            self.objects = basic_search(
                query, cols=self.cols, order_by=order_by, direction=direction,
                limit=limit, offset=offset
            )
            self.filtered_records = get_filtered_count(query)
            self.log_query(query)
        else:
            self.objects = basic_search(
                query, cols=self.cols, order_by=order_by, direction=direction,
                all_samples=True, limit=limit, offset=offset)

    def log_query(self, query):
        """Store the query for improvement purposes."""
        try:
            obj = History.objects.get(query=query)
            obj.count += 1
            obj.save()
        except History.DoesNotExist:
            obj = History.objects.create(query=query, count=1)

    def get_json_response(self):
        data = [
            map(lambda field: obj[field], self.cols)
            for obj in self.objects
        ]

        # define response
        json_response = {
            'data': data,
            'recordsTotal': self.total_records,
            'recordsFiltered': self.filtered_records,
        }

        # serialize to json
        s = StringIO()
        json.dump(json_response, s, cls=DjangoJSONEncoder)
        s.seek(0)
        return s.read()
