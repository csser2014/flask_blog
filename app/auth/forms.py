#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, ValidationError
from wtforms.validators import Required, Length, Regexp
from flask import session
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField(u'用户名', validators=[
        Required(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
               0,
               u'用户名必须是字母, 数字或者下划线')
    ])
    password = PasswordField(u'密码', validators=[Required()])
    recaptcha = StringField(u'验证码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')

    def validate_recaptcha(self, field):
        if session.get('S_RECAPTCHA') != field.data.upper():
            raise ValidationError(u'验证码错误')
