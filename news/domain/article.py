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
    def _create_article_object_for_db(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": {
                "short": self.title
            },
            "description": {
                "long": self.description
            },
            "dates": {
                "posted": int(self.date)
            }
        }
