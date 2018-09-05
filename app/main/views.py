#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import main
from .. import cache
from ..utils import feeds
from .forms import SearchForm
from ..models import User, Category, Tag, Post, Type
from flask import render_template, redirect, url_for, abort


# 首页
@main.route('/', methods=['GET', 'POST'])
@main.route('/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='index_%s')
def index(page=1):
    form = SearchForm()
    pagination = Post.query.filter_by(review=True).\
        order_by(Post.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template(
        'main/index.html',
        pagination=pagination,
        posts=posts,
        form=form
    )


# 搜索
@main.route('/lookup', methods=['GET', 'POST'])
def lookup():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.searchName.data
        return redirect(url_for('main.search', query=query))


@main.route('/search/<string:query>', methods=['GET', 'POST'])
@main.route('/search/<string:query>/page/<int:page>', methods=['GET', 'POST'])
def search(query, page=1):
    form = SearchForm()
    pagination = Post.query.whoosh_search(query, like=True).\
        paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template(
        'main/filter.html',
        type='search',
        posts=posts,
        form=form,
        query=query,
        pagination=pagination
    )


# 详细页
@main.route('/post/<string:slug>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='post_%s')
def post(slug):
    form = SearchForm()
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    return render_template(
        'main/post.html',
        post=post,
        form=form
    )


# 分类
@main.route('/category/<string:slug>', methods=['GET', 'POST'])
@main.route('/category/<string:slug>/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='category_%s')
def category(slug, page=1):
    form = SearchForm()
    category = Category.query.filter_by(slug=slug).first()
    if not category:
        abort(404)
    pagination = category.posts.filter_by(review=True).\
        order_by(Post.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template(
        'main/filter.html',
        type='category',
        category=category,
        posts=posts,
        form=form,
        pagination=pagination
    )


# 标签
@main.route('/tag/<string:slug>', methods=['GET', 'POST'])
@main.route('/tag/<string:slug>/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='tag_%s')
def tag(slug, page=1):
    form = SearchForm()
    tag = Tag.query.filter_by(slug=slug).first()
    if not tag:
        abort(404)
    pagination = tag.posts.filter_by(review=True).\
        order_by(Post.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template(
        'main/filter.html',
        type='tag',
        tag=tag,
        posts=posts,
        form=form,
        pagination=pagination
    )


# 所有标签
@main.route('/tags', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='tags')
def tags():
    form = SearchForm()
    tags = Tag.query.order_by(Tag.id.desc()).all()
    return render_template(
        'main/tags.html',
        tags=tags,
        form=form
    )


# 归档
@main.route('/archive', methods=['GET', 'POST'])
@main.route('/archive/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='archive_%s')
def archive(page=1):
    form = SearchForm()
    pagination = Post.query.filter_by(review=True).\
        order_by(Post.publish_date.desc()).paginate(
            page, per_page=10, error_out=False
        )
    posts = pagination.items
    count = Post.query.filter_by(review=True).count()
    return render_template(
        'main/archive.html',
        posts=posts,
        pagination=pagination,
        form=form,
        count=count
    )


# 链接
@main.route('/links', methods=['GET', 'POST'])
@main.route('/links/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='links_%s')
def links(page=1):
    form = SearchForm()
    pagination = Type.query.order_by(Type.order.desc()).paginate(
        page, per_page=10, error_out=False
    )
    types = pagination.items
    return render_template(
        'main/links.html',
        types=types,
        pagination=pagination,
        form=form
    )


# 作者
@main.route('/user/<string:name>', methods=['GET', 'POST'])
@main.route('/user/<string:name>/page/<int:page>', methods=['GET', 'POST'])
@cache.cached(timeout=3600, key_prefix='user_%s')
def user(name, page=1):
    form = SearchForm()
    user = User.query.filter_by(name=name).first()
    if not user:
        abort(404)
    pagination = user.posts.filter_by(review=True).\
        order_by(Post.id.desc()).paginate(
            page, per_page=10, error_out=False
        )
    posts = pagination.items
    return render_template(
        'main/filter.html',
        form=form,
        type='user',
        user=user,
        pagination=pagination,
        posts=posts
    )


# 关于
@main.route('/about')
def about():
    form = SearchForm()
    return render_template('main/about.html', form=form)


# 与我联系
@main.route('/contact')
def contact():
    form = SearchForm()
    return render_template('main/contact.html', form=form)


# rss订阅
@main.route('/feed')
def feed():
    return feeds.generate_feed().get_response()


'''
@main.route('/clear')
def clear():
    cache.clear()
'''
