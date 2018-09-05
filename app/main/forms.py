#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class SearchForm(FlaskForm):
    searchName = StringField(u'搜索', validators=[Required()])
    submit = SubmitField(u'搜索')
