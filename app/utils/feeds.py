#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from ..models import Post


def make_external(url):
    return urljoin(request.url_root, url)


def generate_feed(feed_page=10):
    feed = AtomFeed(
        u'最新文章',
        feed_url=request.url,
        url=request.url_root
    )

    posts = Post.query.order_by(Post.publish_date.desc()).limit(feed_page).all()

    for post in posts:
        feed.add(
            post.title,
            unicode(post.content_html),
            content_type='html',
            author=post.author.username,
            url=make_external('/post/' + str(post.slug)),
            updated=post.publish_date,
            published=post.publish_date
        )

    return feed
