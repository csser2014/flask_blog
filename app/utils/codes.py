#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import random
import os

rootdir = os.path.join(
    os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)


class RandomChar(object):
    @staticmethod
    def generate_char():
        val = random.randint(65, 90)
        return unichr(val)


class ImageChar():
    def __init__(self, fontColor=(0, 0, 0),
                 size=(80, 40),
                 fontPath=os.path.join(rootdir, 'static/fonts/Ubuntu-B.ttf'),
                 bgColor=(255, 255, 255, 255),
                 fontSize=20):
        self.size = size
        self.fontPath = fontPath
        self.bgColor = bgColor
        self.fontSize = fontSize
        self.fontColor = fontColor
        self.font = ImageFont.truetype(self.fontPath, self.fontSize)
        self.image = Image.new('RGB', size, bgColor)

    def drawText(self, pos, txt, fill):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, txt, font=self.font, fill=fill)
        del draw

    def randRGB(self):
        return (random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))

    def randPoint(self):
        (width, height) = self.size
        return (random.randint(0, width), random.randint(0, height))

    def randLine(self, num):
        draw = ImageDraw.Draw(self.image)
        for i in range(0, num):
            draw.line([self.randPoint(), self.randPoint()], self.randRGB())
        del draw

    def randChinese(self, num):
        gap = 0
        start = 0
        strRes = ''
        for i in range(0, num):
            char = RandomChar().generate_char()
            strRes += char
            x = start + self.fontSize * i + random.randint(0, gap) + gap * i
            self.drawText((x, random.randint(-5, 5)), char, (0, 0, 0))
        self.randLine(8)
        return strRes, self.image
