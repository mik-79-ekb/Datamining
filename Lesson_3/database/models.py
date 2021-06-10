from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    BigInteger,
    Table
)

Base = declarative_base()

tag_post = Table('tags_posts', Base.metadata,
                 Column('tag_id', Integer, ForeignKey('tag.id')),
                 Column('post_id', Integer, ForeignKey('post.id'))
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    url = Column(String(2048), nullable=False, unique=True)
    title = Column(String, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="posts")
    tags = relationship("Tag", secondary=tag_post, back_populates="posts")


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(250), nullable=False, unique=False)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    name = Column(String(250), nullable=False, unique=True)
    posts = relationship("Post", secondary=tag_post, back_populates="tags")


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    text = Column(String(2048), nullable=False, unique=False)
    parent_id = Column(BigInteger, nullable=True, unique=False)
    root_comment_id = Column(BigInteger, nullable=True, unique=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="comment")
    post = relationship("Post", backref="post")