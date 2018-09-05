#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .forms import RoleForm, UserForm, CategoryForm, TagForm,\
    PostForm, LinkForm, ChangePasswordForm, TypeForm
from flask import render_template, redirect, url_for, \
    flash, current_app, request, jsonify
from ..models import Role, User, Category, Tag, Post,\
    Comment, Link, Type
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from ..decorators import clear_cache
from pypinyin import lazy_pinyin
from datetime import datetime
from random import randint
from .. import cache
from . import admin
from .. import db
import time
import os


ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png', 'bmp', 'webp'])


# 首页
@admin.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('admin/index.html')


# 角色列表
@admin.route('/role', methods=['GET', 'POST'])
@admin.route('/role/<int:page>', methods=['GET', 'POST'])
@login_required
def role(page=1):
    pagination = Role.query.order_by(Role.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    roles = pagination.items
    return render_template(
        'admin/role.html',
        pagination=pagination,
        roles=roles
    )


# 新增角色
@admin.route('/role/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_role():
    listurl = 'admin.role'
    addurl = 'admin.add_role'
    form = RoleForm()
    if form.validate_on_submit():
        name = form.name.data
        default = form.default.data
        permission = form.permission.data
        role = Role(
            name=name,
            default=default,
            permission=permission
        )
        db.session.add(role)
        db.session.commit()
        flash(u'添加角色成功')
        return redirect(url_for('admin.role'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除角色
@admin.route('/role/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_role(id):
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash(u'删除角色成功')
    return redirect(url_for('admin.role'))


# 修改角色
@admin.route('/role/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_role(id):
    listurl = 'admin.role'
    addurl = 'admin.add_role'
    editurl = 'admin.edit_role'
    form = RoleForm()
    role = Role.query.get_or_404(id)
    if form.validate_on_submit():
        role.name = form.name.data
        role.default = form.default.data
        role.permission = form.permission.data
        db.session.add(role)
        db.session.commit()
        flash(u'修改角色成功')
        return redirect(url_for('admin.role'))
    form.name.data = role.name
    form.default.data = role.default
    form.permission.data = role.permission
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 用户列表
@admin.route('/user', methods=['GET', 'POST'])
@admin.route('/user/<int:page>', methods=['GET', 'POST'])
@login_required
def user(page=1):
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    users = pagination.items
    return render_template(
        'admin/user.html',
        pagination=pagination,
        users=users
    )


# 新增用户
@admin.route('/user/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_user():
    listurl = 'admin.user'
    addurl = 'admin.add_user'
    form = UserForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        confirmed = form.confirmed.data
        name = form.name.data
        location = form.location.data
        about_me = form.about_me.data
        role_id = form.role.data
        user = User(
            email=email,
            username=username,
            confirmed=confirmed,
            name=name,
            location=location,
            about_me=about_me,
            role=Role.query.get_or_404(int(role_id))
        )
        db.session.add(user)
        db.session.commit()
        flash(u'添加用户成功')
        return redirect(url_for('admin.user'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除用户
@admin.route('/user/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(u'删除用户成功')
    return redirect(url_for('admin.user'))


# 修改用户
@admin.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_user(id):
    listurl = 'admin.user'
    addurl = 'admin.add_user'
    editurl = 'admin.edit_user'
    form = UserForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.role_id = form.role.data
        db.session.add(user)
        db.session.commit()
        flash(u'修改用户成功')
        return redirect(url_for('admin.user'))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.role.data = user.role_id
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 分类列表
@admin.route('/category', methods=['GET', 'POST'])
@admin.route('/category/<int:page>', methods=['GET', 'POST'])
@login_required
def category(page=1):
    pagination = Category.query.order_by(Category.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    categories = pagination.items
    return render_template(
        'admin/category.html',
        pagination=pagination,
        categories=categories
    )


# 新增分类
@admin.route('/category/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_category():
    listurl = 'admin.category'
    addurl = 'admin.add_category'
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        slug = form.slug.data
        description = form.description.data
        category = Category(
            name=name,
            slug=slug,
            description=description
        )
        db.session.add(category)
        db.session.commit()
        flash(u'添加分类成功')
        return redirect(url_for('admin.category'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除分类
@admin.route('/category/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash(u'删除分类成功')
    return redirect(url_for('admin.category'))


# 修改分类
@admin.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_category(id):
    listurl = 'admin.category'
    addurl = 'admin.add_category'
    editurl = 'admin.edit_category'
    form = CategoryForm()
    category = Category.query.get_or_404(id)
    if form.validate_on_submit():
        category.name = form.name.data
        category.slug = form.slug.data
        category.description = form.description.data
        db.session.add(category)
        db.session.commit()
        flash(u'修改分类成功')
        return redirect(url_for('admin.category'))
    form.name.data = category.name
    form.slug.data = category.slug
    form.description.data = category.description
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 标签列表
@admin.route('/tag', methods=['GET', 'POST'])
@admin.route('/tag/<int:page>', methods=['GET', 'POST'])
@login_required
def tag(page=1):
    pagination = Tag.query.order_by(Tag.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    tags = pagination.items
    return render_template(
        'admin/tag.html',
        pagination=pagination,
        tags=tags
    )


def getRandomColor():
    return '#%02X%02X%02X' % (randint(0, 255), randint(0, 255), randint(0, 255))


# 新增标签
@admin.route('/tag/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_tag():
    listurl = 'admin.tag'
    addurl = 'admin.add_tag'
    form = TagForm()
    if form.validate_on_submit():
        name = form.name.data
        slug = form.slug.data
        description = form.description.data
        color = getRandomColor()
        tag = Tag(
            name=name,
            slug=slug,
            description=description,
            color=color
        )
        db.session.add(tag)
        db.session.commit()
        flash(u'添加标签成功')
        return redirect(url_for('admin.tag'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除标签
@admin.route('/tag/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(u'删除标签成功')
    return redirect(url_for('admin.tag'))


# 修改标签
@admin.route('/tag/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_tag(id):
    listurl = 'admin.tag'
    addurl = 'admin.add_tag'
    editurl = 'admin.edit_tag'
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.slug = form.slug.data
        tag.description = form.description.data
        tag.color = getRandomColor()
        db.session.add(tag)
        db.session.commit()
        flash(u'修改标签成功')
        return redirect(url_for('admin.tag'))
    form.name.data = tag.name
    form.slug.data = tag.slug
    form.description.data = tag.description
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 文章列表
@admin.route('/post', methods=['GET', 'POST'])
@admin.route('/post/<int:page>', methods=['GET', 'POST'])
@login_required
def post(page=1):
    pagination = Post.query.order_by(Post.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template(
        'admin/post.html',
        pagination=pagination,
        posts=posts
    )


# 新增文章
@admin.route('/post/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_post():
    listurl = 'admin.post'
    addurl = 'admin.add_post'
    form = PostForm()
    if form.validate_on_submit():
        arrTag = []
        slug = form.slug.data
        title = form.title.data
        sub_title = form.sub_title.data
        description = form.description.data
        content = form.content.data
        source = form.source.data
        click = form.click.data
        review = form.review.data
        recommend = form.recommend.data
        order = form.order.data
        author_id = form.author.data
        category_id = form.category.data
        for tag_id in form.tag.data:
            tag = Tag.query.filter_by(id=tag_id).first()
            arrTag.append(tag)

        post = Post(
            slug=slug,
            title=title,
            sub_title=sub_title,
            description=description,
            content=content,
            source=source,
            click=click,
            review=review,
            recommend=recommend,
            order=order,
            author=User.query.get_or_404(int(author_id)),
            category=Category.query.get_or_404(int(category_id)),
            tags=arrTag
        )
        db.session.add(post)
        db.session.commit()
        flash(u'添加文章成功')
        return redirect(url_for('admin.post'))
    return render_template(
        'admin/add_post.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除文章
@admin.route('/post/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash(u'删除文章成功')
    return redirect(url_for('admin.post'))


# 修改文章
@admin.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_post(id):
    listurl = 'admin.post'
    addurl = 'admin.add_post'
    editurl = 'admin.edit_post'
    form = PostForm()
    post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        arrTag = []
        post.slug = form.slug.data
        post.title = form.title.data
        post.sub_title = form.sub_title.data
        post.description = form.description.data
        post.content = form.content.data
        post.source = form.source.data
        post.click = form.click.data
        post.review = form.review.data
        post.recommend = form.recommend.data
        post.order = form.order.data
        post.author_id = form.author.data
        post.category_id = form.category.data
        for tag_id in form.tag.data:
            tag = Tag.query.filter_by(id=tag_id).first()
            arrTag.append(tag)

        post.tags = arrTag

        db.session.add(post)
        db.session.commit()
        flash(u'修改文章成功')
        return redirect(url_for('admin.post'))
    form.slug.data = post.slug
    form.title.data = post.title
    form.sub_title.data = post.sub_title
    form.description.data = post.description
    form.content.data = post.content
    form.source.data = post.source
    form.click.data = post.click
    form.review.data = post.review
    form.recommend.data = post.recommend
    form.order.data = post.order
    form.author.data = post.author_id
    form.category.data = post.category_id
    return render_template(
        'admin/edit_post.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 评论列表
@admin.route('/comment', methods=['GET', 'POST'])
@admin.route('/comemnt/<int:page>', methods=['GET', 'POST'])
@login_required
def comment(page=1):
    pagination = Comment.query.order_by(Comment.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    comments = pagination.items
    return render_template(
        'admin/comment.html',
        pagination=pagination,
        comments=comments
    )


# 新增评论
@admin.route('/comment/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_comment():
    pass


# 删除评论
@admin.route('/comment/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_comment(id):
    pass


# 修改评论
@admin.route('/comment/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_comment(id):
    pass


# 栏目列表
@admin.route('/type', methods=['GET', 'POST'])
@admin.route('/type/<int:page>', methods=['GET', 'POST'])
@login_required
def type(page=1):
    pagination = Type.query.order_by(Type.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    types = pagination.items
    return render_template(
        'admin/type.html',
        pagination=pagination,
        types=types
    )


# 新增栏目
@admin.route('/type/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_type():
    listurl = 'admin.type'
    addurl = 'admin.add_type'
    form = TypeForm()
    if form.validate_on_submit():
        order = form.order.data
        name = form.name.data
        slug = form.slug.data
        show = form.show.data
        description = form.description.data
        aType = Type(
            order=order,
            name=name,
            slug=slug,
            show=show,
            description=description
        )
        db.session.add(aType)
        db.session.commit()
        flash(u'添加栏目成功')
        return redirect(url_for('admin.type'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除栏目
@admin.route('/type/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_type(id):
    aType = Type.query.get_or_404(id)
    db.session.delete(aType)
    db.session.commit()
    flash(u'删除栏目成功')
    return redirect(url_for('admin.type'))


# 修改栏目
@admin.route('/type/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_type(id):
    listurl = 'admin.type'
    addurl = 'admin.add_type'
    editurl = 'admin.edit_type'
    form = TypeForm()
    aType = Type.query.get_or_404(id)
    if form.validate_on_submit():
        aType.order = form.order.data
        aType.name = form.name.data
        aType.slug = form.slug.data
        aType.show = form.show.data
        aType.description = form.description.data
        db.session.add(aType)
        db.session.commit()
        flash(u'修改栏目成功')
        return redirect(url_for('admin.type'))
    form.order.data = aType.order
    form.name.data = aType.name
    form.slug.data = aType.slug
    form.show.data = aType.show
    form.description.data = aType.description
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


# 友情链接列表
@admin.route('/link', methods=['GET', 'POST'])
@admin.route('/link/<int:page>', methods=['GET', 'POST'])
@login_required
def link(page=1):
    pagination = Link.query.order_by(Link.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    links = pagination.items
    return render_template(
        'admin/link.html',
        pagination=pagination,
        links=links
    )


# 新增友情链接
@admin.route('/link/add', methods=['GET', 'POST'])
@clear_cache
@login_required
def add_link():
    listurl = 'admin.link'
    addurl = 'admin.add_link'
    form = LinkForm()
    if form.validate_on_submit():
        url = form.url.data
        imgUrl = form.imgUrl.data
        name = form.name.data
        description = form.description.data
        order = form.order.data
        type_id = form.aType.data
        link = Link(
            url=url,
            imgUrl=imgUrl,
            name=name,
            description=description,
            order=order,
            type=Type.query.get_or_404(int(type_id))
        )
        db.session.add(link)
        db.session.commit()
        flash(u'添加友情链接成功')
        return redirect(url_for('admin.link'))
    return render_template(
        'admin/add_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl
    )


# 删除友情链接
@admin.route('/link/del/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def del_link(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    flash(u'删除友情链接成功')
    return redirect(url_for('admin.link'))


# 修改友情链接
@admin.route('/link/edit/<int:id>', methods=['GET', 'POST'])
@clear_cache
@login_required
def edit_link(id):
    listurl = 'admin.link'
    addurl = 'admin.add_link'
    editurl = 'admin.edit_link'
    form = LinkForm()
    link = Link.query.get_or_404(id)
    if form.validate_on_submit():
        link.url = form.url.data
        link.imgUrl = form.imgUrl.data
        link.name = form.name.data
        link.description = form.description.data
        link.order = form.order.data
        link.type_id = form.aType.data
        db.session.add(link)
        db.session.commit()
        flash(u'修改友情链接成功')
        return redirect(url_for('admin.link'))
    form.url.data = link.url
    form.imgUrl.data = link.imgUrl
    form.name.data = link.name
    form.description.data = link.description
    form.order.data = link.order
    form.aType.data = link.type_id
    return render_template(
        'admin/edit_form.html',
        form=form,
        listurl=listurl,
        addurl=addurl,
        editurl=editurl
    )


@login_required
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 上传图片
@admin.route('/upload', methods=['POST'])
@login_required
def upload():
    if request.method == 'POST':
        imageFile = request.files.get('editormd-image-file')
        if imageFile and allowed_file(imageFile.filename):
            filename = secure_filename(imageFile.filename)
            if not filename:
                res = {
                    'success': 0,
                    'message': u'图片上传失败'
                }
            else:
                if filename in ['jpg', 'jpeg', 'gif', 'png', 'bmp', 'webp']:
                    uFileName = imageFile.filename
                    name = uFileName.split('.')[0]
                    ext = uFileName.split('.')[1]
                    filename = '_'.join(lazy_pinyin(name)) + '.' + ext

                ext = filename.rsplit('.', 1)[1]
                unix_time = int(time.time())
                new_filename = str(unix_time) + '.' + ext

                # 根据年月日上传图片
                dt = datetime.now()
                today = dt.strftime("%Y-%m-%d")
                file_dir = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                        today)

                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)

                destfile = os.path.join(os.path.join(
                    current_app.config['UPLOAD_URL'], today),
                    new_filename
                )

                imageFile.save(os.path.join(file_dir, new_filename))

                res = {
                    'success': 1,
                    'message': u'图片上传成功',
                    'url': url_for('static', filename=destfile)
                }

    return jsonify(res)


# 修改密码
@admin.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'修改密码成功')
        else:
            flash(u'无效密码')
    return render_template('admin/change_password.html', form=form)


@admin.route('/clear')
@login_required
def clear():
    cache.clear()
