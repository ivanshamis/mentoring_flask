from http import HTTPStatus

from flask import request

from http_utils import ResponseError


def paginate(results, url):
    start = int(request.args.get('start', 1))
    limit = int(request.args.get('limit', 10))
    count = len(results)
    if count < start or limit < 0:
        raise ResponseError(status=HTTPStatus.NOT_FOUND, message="Not found")
    obj = {'start': start, 'limit': limit, 'count': count}
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    obj['results'] = [i.serialize for i in results[(start - 1):(start - 1 + limit)]]
    return obj


def get_filters(filter_fields: list, default_filter: dict):
    filters = default_filter.copy()
    for field in filter_fields:
        value = request.args.get(field)
        if value:
            filters.update({field: value})
    return filters


def get_ordering(ordering_fields: list, table):
    ordering = []
    order_request = request.args.get("order", "").split(",")
    for field in ordering_fields:
        if field in order_request:
            ordering.append(getattr(table, field))
        elif f"-{field}" in order_request:
            ordering.append(getattr(table, field).desc())
    return ordering
