"""A collection of custom validators for user input."""
from django.conf import settings

def validate_list_of_ids(data, field='ids',
                         max_query=settings.MAX_IDS_PER_QUERY):
    """Test excpected list of ids is in valid format."""
    msg = None
    error = False
    if field not in data:
        error = True
        msg = "IDs must be in an array named {0}".format(field)
    elif type(data[field]) is not list:
        error = True
        msg = "IDs must be in an array. Got {0}".format(type(data[field]))
    elif not all(isinstance(i, int) for i in data[field]):
        error = True
        msg = "IDs must be an array of integers."
    elif len(data[field]) > max_query:
        error = True
        msg = "Maxmium of {0} IDs allowed per query.".format(max_query)

    return {"has_errors":error, "message": msg}