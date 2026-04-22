from sqlalchemy.orm import Query


def paginate_query(query: Query, page: int, size: int) -> tuple[list, dict]:
    total = query.order_by(None).count()
    items = query.offset((page - 1) * size).limit(size).all()
    total_pages = (total + size - 1) // size if total else 0

    pagination = {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages,
    }

    return items, pagination


def paginate_data(query: Query, page: int, size: int, data_func) -> dict:
    items, pagination = paginate_query(query, page, size)
    return {
        "data": [data_func(item) for item in items],
        "pagination": pagination,
    }
