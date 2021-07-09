from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class Database:

    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, filter_field, data):
        instance = session.query(model).filter(
            getattr(model, filter_field) == data[filter_field]).first()
        if not instance:
            instance = model(**data)
        return instance

    def add_post(self, data):
        session = self.maker(autoflush=False)
        author = self.get_or_create(session, models.Author, "url", data['author_data'])
        session.add(author)
        post = self.get_or_create(session, models.Post, "id", data["post_data"])

        tags = []
        for t in data['tags_data']:
            tag = self.get_or_create(session, models.Tag, "name", t)
            tags.append(tag)
            session.add(tag)

        comments = []
        for c in data['comments_data']:
            comment_author = self.get_or_create(session, models.Author, "url", c['author_data'])
            comment = self.get_or_create(session, models.Comment, "id", c['comment_data'])
            comment.author = comment_author
            comment.post = post
            comments.append(comment)
            session.add(comment)

        post.author = author
        post.tags = tags
        session.add(post)
        try:
            session.commit()
            print("Committed")
        except Exception as ex:
            session.rollback()
            print(f"Rollback. Exception: {ex}")
        finally:
            session.close()