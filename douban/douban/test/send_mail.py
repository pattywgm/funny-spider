#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: send_mail.py
@time: 17/10/16  下午6:28
@desc: 
"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

MAIL_HOST = 'smtp.exmail.qq.com'
MAIL_FROM = 'crawler@ruyi.ai'
MAIL_USER = 'crawler@ruyi.ai'
MAIL_PASS = 'Shu12349'
MAIL_PORT = 25
MAIL_SSL = True

MAIL_TO = ['wugm@ruyi.ai', ]


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(),
                       addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_email(content):
    #
    # 发送普通文本形式的邮件
    # :param content: 邮件正文内容
    # :return:
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(MAIL_FROM)
    msg['To'] = _format_addr(MAIL_TO)
    msg['Subject'] = Header(u'Scrapy数据入库异常报警', 'utf-8').encode()

    server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    server.set_debuglevel(1)
    server.login(MAIL_USER, MAIL_PASS)
    server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
    server.quit()