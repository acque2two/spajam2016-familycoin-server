#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import sqlite3
import threading
import time
import traceback

import psycopg2
# import chardet

from bottle import HTTPResponse
from bottle import get
from bottle import post
from bottle import put
from bottle import request
from bottle import route
from bottle import run

DBNAME = "creas.db"


conn = psycopg2.connect(port=5432, host=CONFIG.DB.HOST, database=CONFIG.DB.DB,
                       user=CONFIG.DB.USER, password=CONFIG.DB.PASSWORD)

# db.createDb(DBNAME)
# conn = sqlite3.connect(DBNAME)

THREAD = threading.Timer(30, conn.commit()).start()

error = HTTPResponse(status=400, body="q is None")
error.set_header("Content-Type", "text/html")


def res(body):
    print(" >>>" + body)
    response = HTTPResponse(status=200, body=body)
    response.set_header("Content-Type", "application/json")
    conn.commit()
    return response


def precheck(body):
    print("Precheck ERROR") if body is None else print(body)
    conn.commit()
    print(body)
    return False if body is None else True


@route('/')
def exec():
    global conn
    body = "This is a SgnzServer_0606"
    res = HTTPResponse(status=200, body=body)
    res.set_header("Content-Type", "text/html")
    conn.commit()
    return res


@post('/')
def exec():
    global conn
    conn.commit()
    return res("you sent " + request.params.get('name'))


# 家族追加
@post('/familyadd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8" )
    f_id = jsondecode['family'][0]['f_id']
    f_name = jsondecode['family'][0]['f_name']
    c = conn.cursor()
    try:
        c.execute("INSERT into family(f_id, f_name) VALUES(%s,%s)", (f_id, f_name))
        status = True
    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 家族削除
@post('/familydel')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    f_name = jsondecode['family'][0]['f_name']

    c = conn.cursor()
    status = True
    try:
        c.execute('DELETE from family WHERE f_id = %s', (f_id,))
    except:
        status = False
    conn.commit()
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))

#家族idの有無
@post('/familyexist')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']

    c = conn.cursor()
    c.execute('SELECT * from family WHERE f_id = %s',
              (f_id, ))
    z = c.fetchall()
    print (z)
    status = True if len(z) >= 1 else False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))



# ユーザー追加
@post('/useradd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    u_name = jsondecode['family'][0]['users'][0]['u_name']
    score = 0
    admin = jsondecode['family'][0]['users'][0]['admin']
    adult = jsondecode['family'][0]['users'][0]['adult']
    sex = jsondecode['family'][0]['users'][0]['sex']
    c = conn.cursor()
    try:
        c.execute("INSERT into users(u_id, u_name, f_id, score, admin, adult, sex) "
                  "VALUES(%s,%s,%s,%s,%s,%s,%s)", (u_id, u_name, f_id, score, admin, adult, sex))
        status = True
    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# ユーザーは本当にいるのか
@post('/userexist')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    u_name = jsondecode['family'][0]['users'][0]['u_name']

    c = conn.cursor()
    c.execute('SELECT * from users WHERE u_id = %s AND u_name = %s',
              (u_id, u_name))
    status = True if len(c.fetchall()) >= 1 else False
    conn.commit()
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# ユーザーの家族IDを取得
@post('/userfamilyget')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    u_id = jsondecode['family'][0]['users'][0]['u_id']

    c = conn.cursor()
    c.execute('SELECT f_id from users WHERE u_id = %s',
              (u_id,))

    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        list.append(dict)
    conn.commit()
    conn.commit()
    return res(json.dumps({'family': list}, ensure_ascii=False))


# ユーザー削除
@post('/userdel')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    u_id = jsondecode['family'][0]['users'][0]['u_id']

    c = conn.cursor()
    status = True
    try:
        c.execute('DELETE from unapproved WHERE u_id = %s', (u_id,))
        c.execute('DELETE from achievement WHERE u_id = %s', (u_id,))
        c.execute('DELETE from users WHERE u_id = %s', (u_id,))
    except:
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))

#スコア変更
@post('/scorechange')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    score = jsondecode['family'][0]['users'][0]['score']

    c = conn.cursor()
    status = True
    try:

        c.execute('update users set score = %s WHERE u_id = %s', (score, u_id))
    except:
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


#全てのデータ
@post('/alldata')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "utf-8")
    f_id = jsondecode['family'][0]['f_id']

    c = conn.cursor()

    c.execute('SELECT * FROM family WHERE f_id = %s', (f_id,))

    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM users where f_id = %s', (dict['f_id'],))
        for j in d.fetchall():
            dict2 = {}
            for k in range(len(d.description)):
                dict2[d.description[k][0]] = j[k]
            dict3 = {}
            e = conn.cursor()
            e.execute('SELECT * FROM unapproved where u_id = %s', (dict2['u_id'],))
            for k in e.fetchall():
                dict3 = {}
                for l in range(len(e.description)):
                    dict3[e.description[l][0]] = k[l]
            dict2['unapproved'] = dict3

            dict3 = {}
            e.execute('SELECT * FROM achievement where u_id = %s', (dict2['u_id'],))

            for k in e.fetchall():
                dict3 = {}
                for l in range(len(e.description)):
                    dict3[e.description[l][0]] = k[l]
            dict2['achievement'] = dict3
            dict2list.append(dict2)

        dict['users']=dict2list
        dict2={}
        dict2list=[]

        d.execute('SELECT * FROM work where f_id = %s', (dict['f_id'],))
        for j in d.fetchall():
            dict2 = {}
            for k in range(len(d.description)):
                dict2[d.description[k][0]] = j[k]
            e.execute('SELECT * FROM genre where g_id = %s', (dict2['g_id'],))
            for k in e.fetchall():
                dict3 = {}
                for l in range(len(e.description)):
                    dict3[e.description[l][0]] = k[l]
                dict2['genre'] = dict3
            dict2list.append(dict2)
        dict['work']=dict2list

        dict2 = {}
        e = conn.cursor()
        e.execute('SELECT * FROM genre', ("",))

        dict2list = []
        for k in e.fetchall():
            dict2 = {}
            for l in range(len(e.description)):
                dict2[e.description[l][0]] = k[l]
            dict2list.append(dict2)
        dict['genre'] = dict2list

        dict2 = {}
        f = conn.cursor()
        f.execute('SELECT * FROM product where f_id = %s',  (dict['f_id'],))
        for k in f.fetchall():
            dict2 = {}
            for l in range(len(e.description)):
                dict2[e.description[l][0]] = k[l]
            dict['product'] = dict2

        list.append(dict)

    print({'family': list})
    return res(json.dumps({'family': list}, ensure_ascii=False))


# 仕事削除
@post('/workdel')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    w_name = jsondecode['family'][0]['work'][0]['w_name']

    c = conn.cursor()
    status = True
    try:
        c.execute('DELETE from work WHERE w_name = %s and f_id' , (w_name, f_id))
    except:
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 仕事追加
@post('/workadd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error
    jsondecode = json.loads(request.params.q, "UTF-8")

    g_id = jsondecode['family'][0]['work'][0]['genre']['g_id']
    f_id = jsondecode['family'][0]['f_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    w_name = jsondecode['family'][0]['work'][0]['w_name']
    w_text = jsondecode['family'][0]['work'][0]['w_text']
    point = jsondecode['family'][0]['work'][0]['point']
    image = jsondecode['family'][0]['work'][0]['image']

    c = conn.cursor()
    try:
        c.execute("INSERT INTO work(g_id, f_id, u_id, w_name, w_text,"
                  "point, image) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                  (g_id, f_id, u_id, w_name, w_text, point, image))
        conn.commit()

        status = True
    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# ジャンル一覧
@post('/genrelist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    # jsondecode = json.loads(request.params.q, "UTF-8")

    c = conn.cursor()
    c.execute('SELECT * FROM genre')

    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': ({'work': ({'genre': list})})}, ensure_ascii=False))


# ジャンル検索
@post('/workgenrelist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    g_id = jsondecode['family'][0]['work'][0]['genre']['g_id']
    f_id = jsondecode['family'][0]['f_id']

    c = conn.cursor()

    c.execute('SELECT * FROM work WHERE g_id = %s and f_id = %s', (g_id,f_id))

    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        list.append(dict)
    if len(list) == 0:
        list.append({})
    conn.commit()
    return res(json.dumps({'family': [{'work': list}]}, ensure_ascii=False))


# 家族情報で取得
@post('/usersfamilyget')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    # jsondecode = json.loads(request.params.q, "UTF-8")
    # search = jsondecode['search']

    c = conn.cursor()

    c.execute('SELECT * FROM users')
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM users where f_id = %s order by point desc' , (dict['f_id'],))
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[j][0]] = i[j]
            dict2list.append(dict2)
        dict['users'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': list}, ensure_ascii=False))


# 仕事一覧
@post('/worklist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']

    c = conn.cursor()

    c.execute('SELECT * FROM work where f_id = %s', (f_id,))
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM genre where g_id = %s', (dict['g_id'],))
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[d.description[k][0]] = j[k]
            dict2list.append(dict2)
        dict['genre'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': [{'work': list}]}, ensure_ascii=False))


# 未承認追加
@post('/unapprovedadd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    w_id = jsondecode['family'][0]['work'][0]['w_id']
    date = time.time()
    c = conn.cursor()
    try:
        c.execute("select * from unapproved where f_id = %s and u_id = %s and w_id = %s", (f_id, u_id, w_id))
        if len(c.fetchall()) != 0:
            status = False
            return res(json.dumps({'status': status}, ensure_ascii=False))
        status = True
        c.execute("INSERT into unapproved(f_id, u_id, w_id, date) VALUES(%s,%s,%s,%s)", (f_id, u_id, w_id, date))

    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 未承認一覧
@post('/unapprovedlist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    # jsondecode = json.loads(request.params.q, "UTF-8")
    # search = jsondecode['search']

    c = conn.cursor()

    c.execute('SELECT * FROM unapproved')
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM unapproved order by date DESC limit 25')
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[d.description[k][0]] = j[k]
            dict2list.append(dict2)
        dict['unapproved'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': ({'user': ({'unapproved': list})})}, ensure_ascii=False))


# 未承認削除
@post('/unapproveddel')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    # f_id = jsondecode['family'][0]['f_id']
    f_id = jsondecode['family'][0]['f_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    w_id = jsondecode['family'][0]['work'][0]['w_id']

    c = conn.cursor()
    status = True
    try:
        c.execute('DELETE from unapproved where f_id = %s and u_id = %s and w_id = %s', (f_id, u_id, w_id))
    except:
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 達成追加
@post('/achievementadd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']
    w_id = jsondecode['family'][0]['work'][0]['w_id']
    date = time.time()
    c = conn.cursor()
    try:
        c.execute("INSERT into achievement(f_id, u_id, w_id, date) VALUES(%s,%s,%s,%s)", (f_id, u_id, w_id, date))
        status = True
    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 達成一覧(新着)
@post('/achievementlist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    # jsondecode = json.loads(request.params.q, "UTF-8")
    # search = jsondecode['search']

    c = conn.cursor()

    c.execute('SELECT * FROM achievement')
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM achievement order by date DESC limit 25 ')
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[k][0]] = j[k]
            dict2list.append(dict2)
        dict['achievement'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': [{'work': list}]}, ensure_ascii=False))

#達成一覧(ジャンル別)
@post('/achievementgenrelist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    g_id = jsondecode['family'][0]['work'][0]['genre'][0]['g_id']

    c = conn.cursor()

    c.execute('SELECT * FROM achievement WHERE g_id = %s', (g_id,))
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM achievement limit 25 order by date DESC')
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[j][0]] = i[j]
            dict2list.append(dict2)
        dict['achievement'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family':[{'work': list}]}, ensure_ascii=False))


# 達成一覧(ユーザー別新着)
@post('/achievementuserlist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    u_id = jsondecode['family'][0]['users'][0]['u_id']

    c = conn.cursor()

    c.execute('SELECT * FROM achievement where u_id = %s', (u_id, ))
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM achievement limit 25 order by date DESC')
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[j][0]] = i[j]
            dict2list.append(dict2)
        dict['achievement'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family':[{'work': list}]}, ensure_ascii=False))


# 達成一覧(ユーザー別ジャンル別)
@post('/achievementusergenrelist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    g_id = jsondecode['family'][0]['work'][0]['genre'][0]['g_id']
    u_id = jsondecode['family'][0]['users'][0]['u_id']

    c = conn.cursor()

    c.execute('SELECT * FROM achievement '
              'WHERE u_id = %s and g_id = %s', (u_id, g_id))
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM achievement limit 25 order by date DESC')
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[j][0]] = i[j]
            dict2list.append(dict2)
        dict['achievement'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family':[{'work': list}]}, ensure_ascii=False))



#商品追加
@post('/productadd')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    #p_id = jsondecode['family'][0]['product'][0]['p_id']
    p_name = jsondecode['family'][0]['product'][0]['p_name']
    f_id = jsondecode['family'][0]['f_id']
    p_point = jsondecode['family'][0]['product'][0]['p_point']
    c = conn.cursor()
    try:

        c.execute("INSERT into product( p_name, f_id, p_point)"
                  " VALUES(k%s,%s,%s)", ( p_name, f_id, p_point))
        status = True
    except:
        traceback.print_exc()
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


# 商品一覧
@post('/productlist')
def exec():
    global conn
    if not precheck(request.params.q):
        return error

    # jsondecode = json.loads(request.params.q, "UTF-8")
    # f_id = jsondecode['family'][0]['f_id']

    c = conn.cursor()

    c.execute('SELECT * FROM product ')
    # for i in c.fetchall():
    #     dict[i[0]] = dict[i[1]]
    list = []
    for i in c.fetchall():
        dict = {}
        for j in range(len(c.description)):
            dict[c.description[j][0]] = i[j]
        dict2 = {}
        dict2list = []
        d = conn.cursor()
        d.execute('SELECT * FROM product where f_id = %s '
                  'order by p_point', (dict['f_id'],))
        for j in d.fetchall():
            for k in range(len(d.description)):
                dict2[c.description[k][0]] = j[k]
            dict2list.append(dict2)
        dict['product'] = dict2list

        list.append(dict)

    conn.commit()
    return res(json.dumps({'family': ({'product': list})}, ensure_ascii=False))

#商品削除

@post('/productdel')
def exec():
    global conn
    if not precheck(request):
        return error

    jsondecode = json.loads(request.params.q, "UTF-8")
    f_id = jsondecode['family'][0]['f_id']
    p_id = jsondecode['family'][0]['product'][0]['p_id']

    c = conn.cursor()
    status = True
    try:
        c.execute('DELETE from product where f_id = %s and p_id = %s', (f_id, p_id))
    except:
        status = False
    conn.commit()
    return res(json.dumps({'status': status}, ensure_ascii=False))


@get('/dbGet')
def exec():
    global conn
    conn.commit()
    conn.close()
    res = HTTPResponse(status=200, body=open(DBNAME, mode='rb').read())
    conn = sqlite3.connect(DBNAME)
    conn.commit()
    return res


@put('/image/put')
def exec():
    try:
        hash = hashlib.md5(request.body)
        date = time.time()
        filename = str(date) + '-' + hash
        f = open(filename, "wb")
        f.write(request.body)

    except AssertionError:
        return {
            "error": "Invalid File",
        }
    except AttributeError:
        return {
            "error": "Insufficient Request",
        }

    conn.commit()
    return filename


@get('/image/get')
def exec():
    try:
        filename = request.body
        f = open(filename, "rb")

    except AssertionError:
        return {
            "error": "Invalid File",
        }
    except AttributeError:
        return {
            "error": "Insufficient Request",
        }

    conn.commit()
    return f.read()


run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
