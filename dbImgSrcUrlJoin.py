##!/usr/bin/python
# -*- coding: UTF-8 -*-
import urlparse

from dbHelper import getTmathConnCsor
from framework.htmlParser import getSoupByStr


def handleHtml(baseUrl,htmlContent):
    soup = getSoupByStr(htmlContent)
    modfied = False
    for img in soup.select('img'):
        imgSrc = img['src']
        if not imgSrc.startswith('http'):
            img['src'] = urlparse.urljoin(baseUrl,imgSrc)
            modfied = True
    return unicode(soup),modfied

def cleanHtml(htmlContent):
    soup = getSoupByStr(htmlContent)
    modfied = False
    [a.unwrap() for a in soup.select('a')]

    for img in soup.select('img'):
        if not img.has_key('style') or len(img['style']) < 1:
            img['style'] = 'max-width:100%'
        else:
            preStyle = img['style']
            if preStyle.endswith(';'):
                img['style'] = img['style'] + 'max-width:100%;'
            else:
                img['style'] = img['style'] + ';max-width:100%'

        modfied = True
    return unicode(soup),modfied

def startWithConn(conn, csor,dbName,contentName,baseUrl,carry = 500, begid = -1):
    endId = begid + carry
    updateSql = 'update ' + dbName + ' set ' + contentName + ' = %s where id = %s '
    print updateSql

    csor.execute('select id from ' + dbName + ' order by id desc limit 1')
    count = csor.fetchone()[0]
    if count < carry:
        endId = count
    while endId < count + 1:

        sql = 'select id, ' + contentName + ' from ' + dbName + ' where id > ' + str(begid) + ' and id <= ' + str(endId)
        print 'sql:',sql
        csor.execute(sql)
        conn.commit()
        res = csor.fetchall()
        for rec in res:
            id = rec[0]
            contentHtml = rec[1]
            # newContent,mod = handleHtml(baseUrl,contentHtml)
            newContent,mod = cleanHtml(contentHtml)
            if not mod:
                continue
            csor.execute(updateSql,(newContent,id))
            conn.commit()

        if endId == count:
            break
        begid = endId
        endId = endId + carry
        if endId > count:
            endId = count


if __name__ == '__main__':
    conn,csor = getTmathConnCsor()
    # dbName = 'daily_today'
    dbName = 'daily_news'
    contentName = 'content'
    baseUrl = 'http://www.todayonhistory.com/'
    startWithConn(conn,csor,dbName,contentName,baseUrl,begid=0)