import strawberry
from .resolvers import Query, Mutation

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        strawberry.extensions.QueryDepthLimiter(max_depth=10),
        strawberry.extensions.ValidationCache(maxsize=100),
    ]
) 