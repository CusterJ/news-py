import dataclasses

@dataclasses.dataclass
class Article:
    id: str
    title: str
    description: str
    date: int
    url: str

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
    def to_dict(self):
        return dataclasses.asdict(self)


# a = Article

# a.date = 123
# a.id = "aasdf123"
# a.description = "adescr "
# a.title = "atitle"
# a.url = "aurl"

# print(f"A dict = {a.__dict__}")


# dict = {
#     "id": "bid1234f",
#     "title": "btitle",
#     "description": "bdescr",
#     "date": 4312,
#     "url": "burl",
# }

# b = Article.from_dict(dict)

# print(f"B dict = {b.to_dict()}")

