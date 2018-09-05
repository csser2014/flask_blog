#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, \
    url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from ..utils.codes import ImageChar
from .forms import LoginForm
from ..models import User
from . import auth
import StringIO
from ..email import send_mail


# 登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('admin.index'))
        flash(u'无效的用户名和密码')
    return render_template('auth/login.html', form=form)


# 退出
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm your account', 'auth/email/confirm',
              user=current_user, token=token)
    flash(u'已经用邮箱给你发送了确认的邮件了，请查收')
    return redirect(url_for('admin.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('admin.index'))
    if current_user.confirm(token):
        flash(u'你已经确认了账号，谢谢!')
    else:
        flash(u'这个确认的链接是无效的或者过期的')
    return redirect(url_for('admin.index'))


@auth.route('/code', methods=['GET'])
def generate_code():
    ic = ImageChar(fontColor=(100, 200, 100))
    strs, code_img = ic.randChinese(4)
    session['S_RECAPTCHA'] = strs
    buf = StringIO.StringIO()
    code_img.save(buf, 'JPEG', quality=70)
    buf_str = buf.getvalue()
    response = current_app.make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    return response
