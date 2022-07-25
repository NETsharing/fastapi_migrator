from pydantic.types import ConstrainedInt

from app.schema.response import BaseSchema


class Page(ConstrainedInt):
    ge = 1
    example = 1
    description = "Requested page number"


class MaxPerPage(ConstrainedInt):
    ge = 1
    le = 100
    example = 10
    description = "Maximum number of results on the page"


class TotalCount(ConstrainedInt):
    ge = 0

    example = 10
    description = "Total count of query results"


class PaginationParams(BaseSchema):
    page: Page = Page(1)
    max_per_page: MaxPerPage = MaxPerPage(10)


class Paginator(PaginationParams):
    total_count: TotalCount
