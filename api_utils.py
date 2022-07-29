from flask import request
from pydantic import BaseModel

from extensions import db


def paginate(results: list, url: str, parsed_query: dict) -> dict:
    start = parsed_query["pagination"]["start"]
    limit = parsed_query["pagination"]["limit"]
    previous_url = f"?start={max(1, start - limit)}&limit={limit}" if start > 1 else ""
    next_url = f"?start={start + limit}&limit={limit}" if len(results) == limit else ""
    other_params = parsed_query["filtering"].copy()
    other_params["order"] = parsed_query["order"]
    others = ''.join([f"&{key}={value}" for key, value in other_params.items() if value])
    return {
        "start": start,
        "limit": limit,
        "previous": url + previous_url + others if previous_url else "",
        "next": url + next_url + others if next_url else "",
        "results": [i.serialize for i in results]
    }


def get_ordering(order_request, ordering_fields: list, model):
    ordering = []
    if order_request:
        for field in ordering_fields:
            if field in order_request:
                ordering.append(getattr(model, field))
            elif f"-{field}" in order_request:
                ordering.append(getattr(model, field).desc())
    return ordering


def parse_query(query: BaseModel, model: db.Model, ordering_fields: list, default_filter: dict) -> dict:
    query_dict = {key: value for key, value in query.dict().items() if value}
    order_request = query_dict.pop("order", "")
    filtering = {key: value for key, value in query_dict.items() if value}
    filtering.update(default_filter)
    return {
        "ordering": get_ordering(
            order_request=order_request,
            ordering_fields=ordering_fields,
            model=model,
        ),
        "order": order_request,
        "pagination": {
            "start": query_dict.pop("start", 1),
            "limit": query_dict.pop("limit", 10),
        },
        "filtering": filtering
    }


def generate_response_message(status: int, message: str = "", key: str = "result"):
    return {key: message} if message else "", status


def generate_response_error(status: int, message: str):
    return generate_response_message(status=status, message=message, key="error")
