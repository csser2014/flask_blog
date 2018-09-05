#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField,\
    SelectField, IntegerField, SelectMultipleField, PasswordField
from wtforms.validators import Required, Length, EqualTo
from ..models import Role, User, Category, Tag, Type


# 角色表单
class RoleForm(FlaskForm):
    name = StringField(u'角色名称', validators=[Required(), Length(1, 256)])
    default = BooleanField(u'是否是默认角色', default=False)
    permission = StringField(u'角色权限', validators=[Required(), Length(1, 256)])
    submit = SubmitField(u'确定')


# 用户表单
class UserForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required()])
    username = StringField(u'用户名', validators=[Required()])
    confirmed = BooleanField(u'是否激活', default=False)
    name = StringField(u'姓名', validators=[Required()])
    location = StringField(u'地址', validators=[Required()])
    about_me = TextAreaField(u'关于我', validators=[Required()])
    role = SelectField(u'所属角色', coerce=int, validators=[Required()])
    submit = SubmitField(u'确定')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name)
                             for r in Role.query.order_by(Role.name).all()]


# 分类表单
class CategoryForm(FlaskForm):
    name = StringField(u'标签名称', validators=[Required()])
    slug = StringField(u'自定义url', validators=[Required()])
    description = TextAreaField(u'分类描述')
    submit = SubmitField(u'确定')


# 标签表单
class TagForm(FlaskForm):
    name = StringField(u'标签名称', validators=[Required()])
    slug = StringField(u'自定义url', validators=[Required()])
    description = TextAreaField(u'标签描述')
    submit = SubmitField(u'确定')


# 文章表单
class PostForm(FlaskForm):
    slug = StringField(u'自定义url', validators=[Required()])
    title = StringField(u'标题', validators=[Required()])
    sub_title = StringField(u'副标题', validators=[Required()])
    description = TextAreaField(u'正文描述')
    content = TextAreaField(u'正文', validators=[Required()])
    source = StringField(u'文章来源')
    click = IntegerField(u'点击数', default=0)
    review = BooleanField(u'审核', default=True)
    recommend = BooleanField(u'推荐', default=False)
    order = IntegerField(u'排序', default=0)
    author = SelectField(u'所属用户', coerce=int, validators=[Required()])
    category = SelectField(u'所属分类', coerce=int, validators=[Required()])
    tag = SelectMultipleField(u'标签', coerce=int, validators=[Required()])
    submit = SubmitField(u'确定')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.author.choices = [(u.id, u.name)
                               for u in User.query.order_by(User.name).all()]

        self.category.choices = [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]

        self.tag.choices = [
            (t.id, t.name) for t in Tag.query.order_by(Tag.name).all()
        ]


# 评论表单
class CommentForm(FlaskForm):
    pass


# 栏目表单
class TypeForm(FlaskForm):
    order = IntegerField(u'排序', default=0)
    name = StringField(u'栏目名称', validators=[Required()])
    slug = StringField(u'自定义url', validators=[Required()])
    show = BooleanField(u'是否显示', default=True)
    description = TextAreaField(u'栏目描述')
    submit = SubmitField(u'确定')


# 友情链接表单
class LinkForm(FlaskForm):
    url = StringField(u'友情链接地址', validators=[Required()])
    imgUrl = StringField(u'友情链接图片地址', validators=[Required()])
    name = StringField(u'友情链接名称', validators=[Required()])
    description = TextAreaField(u'友情链接描述', validators=[Required()])
    order = IntegerField(u'友情链接排序', default=0)
    aType = SelectField(u'所属栏目', coerce=int, validators=[Required()])
    submit = SubmitField(u'确定')

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        self.aType.choices = [(t.id, t.name)
                             for t in Type.query.order_by(Type.id).all()]


# 修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(
        u'新密码',
        validators=[
            Required(),
            EqualTo('password2', message=u'再次输入的新密码必须一致')
        ]
    )
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'修改密码')
