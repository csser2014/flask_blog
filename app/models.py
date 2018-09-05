#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from app.pygment import HighlighterRenderer
from sqlalchemy.exc import IntegrityError
from jieba.analyse import ChineseAnalyzer
from flask import current_app, request
from random import seed, randint
from . import db, login_manager
from datetime import datetime
import forgery_py
import hashlib
import misaka as m


# 用户权限
class Permission:
    FOLLOW = 0x01                                               # 0000 0001
    COMMENT = 0x02                                              # 0000 0010
    WRITE_ARTICLES = 0x04                                       # 0000 0100
    MODERATE_COMMENTS = 0x08                                    # 0000 1000
    ADMINISTER = 0x80                                           # 1000 0000


# 角色表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)                # 角色名称
    # 注册用户时选择默认的角色
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)                          # 角色的权限
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __unicode__(self):
        return self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),          # 0000 0111
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),  # 0000 1111
            'Administrator': (0xff, False)                      # 1111 1111
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.permission = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
            db.session.commit()


# 用户表
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)               # 邮箱
    username = db.Column(db.String(64), unique=True)            # 用户名
    password_hash = db.Column(db.String(128))                   # 加密后的密码
    confirmed = db.Column(db.Boolean, default=False)            # 是否邮箱激活
    name = db.Column(db.String(64))                             # 姓名
    location = db.Column(db.String(64))                         # 地址
    about_me = db.Column(db.Text)                               # 关于我
    member_since = db.Column(db.DateTime(),
                             default=datetime.utcnow)
    last_since = db.Column(db.DateTime(),
                           default=datetime.utcnow)             # 最后一次登录
    avatar_hash = db.Column(db.String(32))                      # 头像
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __unicode__(self):
        return self.name

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permisssion=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @staticmethod
    def insert_users(count=10):
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.paragraphs(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # 根据邮箱地址显示gravatar头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    # 更新每次登录时间
    def updateLastTime(self):
        self.last_since = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError(u'密码不是可读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 通过邮箱来激活用户
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    # 通过邮箱重置密码
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.reset != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    # 权限的判断
    def can(self, permission):
        return self.role is not None and \
            (self.role.permission & permission) == permission

    # 是否是管理员
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


# 栏目表
class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, default=0)                    # 排序
    name = db.Column(db.String(256))                            # 栏目名称
    slug = db.Column(db.String(256))                            # 自定义url名称
    show = db.Column(db.Boolean, default=True)                  # 是否显示
    description = db.Column(db.Text())                          # 栏目描述
    links = db.relationship('Link', backref='type', lazy='dynamic')

    def __unicode__(self):
        return self.name

    @staticmethod
    def insert_types(count=10):
        seed()
        for i in range(count):
            t = Type(
                name=forgery_py.lorem_ipsum.word(),
                slug=forgery_py.lorem_ipsum.word(),
                show=True,
                description=forgery_py.lorem_ipsum.paragraphs()
            )
            db.session.add(t)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 分类表
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))                            # 分类名称
    slug = db.Column(db.String(256))                            # 自定义url名称
    description = db.Column(db.Text())                          # 分类描述
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __unicode__(self):
        return self.name

    @staticmethod
    def insert_categories(count=10):
        seed()
        for i in range(count):
            c = Category(
                name=forgery_py.lorem_ipsum.word(),
                slug=forgery_py.lorem_ipsum.word(),
                description=forgery_py.lorem_ipsum.paragraphs()
            )
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 文章表和标签表的多对多的连接关系
posts_tags = db.Table(
    'posts_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)


# 标签表
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))                            # 标签名称
    slug = db.Column(db.String(256))                            # 自定义url名称
    color = db.Column(db.String(256))                           # 标签颜色
    description = db.Column(db.Text())                          # 标签描述

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)

    def __unicode__(self):
        return self.name

    @staticmethod
    def insert_tags(count=10):
        seed()
        for i in range(count):
            t = Tag(
                name=forgery_py.lorem_ipsum.word(),
                slug=forgery_py.lorem_ipsum.word(),
                description=forgery_py.lorem_ipsum.paragraph()
            )
            db.session.add(t)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 文章表
class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'content']
    __analyzer__ = ChineseAnalyzer()
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(256))                            # 自定义url名称
    title = db.Column(db.String(256))                           # 标题
    sub_title = db.Column(db.String(256))                       # 副标题
    description = db.Column(db.Text())                          # 正文描述
    content = db.Column(db.Text())                              # 正文
    source = db.Column(db.String(256))                          # 文章来源
    content_html = db.Column(db.Text())
    publish_date = db.Column(db.DateTime, index=True,
                             default=datetime.utcnow)           # 发布时间
    update = db.Column(db.DateTime, index=True,
                       default=datetime.utcnow)                 # 更新时间
    click = db.Column(db.Integer, default=0)                    # 点击数
    review = db.Column(db.Boolean, default=True)                # 审核, 默认通过
    recommend = db.Column(db.Boolean, default=False)            # 推荐, 默认不推荐
    stick = db.Column(db.Boolean, default=False)                # 置顶, 默认不置顶
    order = db.Column(db.Integer, default=0)                    # 排序
    showImg = db.Column(db.Boolean, default=False)              # 显示图片，默认不显示
    imgName = db.Column(db.String(256))                         # 图片名称
    imgUrl = db.Column(db.String(256))                          # 图片地址
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship(
        'Tag',
        secondary=posts_tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __unicode__(self):
        return self.title

    # 每次更新点击文章的次数
    def update_click(self):
        self.click += 1
        db.session.add(self)
        db.session.commit()

    # 下一篇文章
    def next(self):
        post = Post.query.filter(Post.publish_date > self.publish_date)\
            .order_by(Post.publish_date.asc()).first()
        print '===='
        print post
        print '===='
        if post:
            return post
        else:
            return None

    # 上一篇文章
    def prev(self):
        post = Post.query.filter(Post.publish_date < self.publish_date)\
            .order_by(Post.publish_date.desc()).first()
        if post:
            return post
        else:
            return None

    # 相关文章
    def relativePost(self):
        relateTag = self.tags
        if (len(relateTag) > 0):
            tag = relateTag[randint(0, len(relateTag) - 1)]
            posts = tag.posts.filter(Post.title != self.title)\
                .order_by(Post.publish_date.desc()).limit(10).all()
            return posts
        return None

    @staticmethod
    def insert_posts(count=100):
        seed()
        user_count = User.query.count()
        category_count = Category.query.count()
        tag_count = Tag.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            c = Category.query.offset(randint(0, category_count - 1)).first()
            tags = [Tag.query.offset(randint(0, tag_count - 1)).first()
                    for i in range(0, randint(1, 5))]
            p = Post(
                slug=forgery_py.lorem_ipsum.word(),
                title=forgery_py.lorem_ipsum.title(),
                sub_title=forgery_py.lorem_ipsum.title(),
                description=forgery_py.currency.description(),
                content=forgery_py.lorem_ipsum.paragraphs(),
                content_html=forgery_py.lorem_ipsum.paragraph(),
                source='unknow',
                publish_date=forgery_py.date.date(True),
                author=u,
                category=c,
                tags=tags
            )
            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        renderer = HighlighterRenderer()
        md = m.Markdown(renderer=renderer, extensions=('fenced-code', 'tables'))
        target.content_html = md(value)


# 评论表
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())                              # 评论内容
    username = db.Column(db.String(256))                        # 用户名
    publish_date = db.Column(db.DateTime, index=True,
                             default=datetime.utcnow)           # 发布时间
    disabled = db.Column(db.Boolean, default=False)             # 是否禁止评论
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __unicode__(self):
        return self.username

    @staticmethod
    def insert_comments(count=10):
        seed()
        post_count = Post.query.count()
        for i in range(count):
            p = Post.query.offset(randint(0, post_count - 1)).first()
            c = Comment(
                content=forgery_py.lorem_ipsum.paragraphs(),
                username=forgery_py.lorem_ipsum.word(),
                publish_date=forgery_py.date.date(True),
                post=p
            )
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 友情链接
class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))                             # 友情链接地址
    imgUrl = db.Column(db.String(256))                          # 友情链接图片地址
    name = db.Column(db.String(256))                            # 友情链接名称
    description = db.Column(db.Text())                          # 友情链接描述
    order = db.Column(db.Integer, default=0)                    # 友情链接排序
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'))

    def __unicode__(self):
        return self.name

    @staticmethod
    def insert_links(count=10):
        seed()
        type_count = Type.query.count()
        for i in range(count):
            t = Type.query.offset(randint(0, type_count - 1)).first()
            l = Link(
                url='http://www.baidu.com',
                imgUrl='http://www.baidu.com',
                name=forgery_py.lorem_ipsum.word(),
                description=forgery_py.lorem_ipsum.paragraphs(),
                type=t
            )
            db.session.add(l)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


# 网站SEO
# class SEO(db.Model):
    # pass

class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


# 使用 login-login 自动加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.event.listen(Post.content, 'set', Post.on_changed_content)
