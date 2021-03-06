# coding=utf-8
# author:u'王健'
#Date: 14-3-9
#Time: 下午3:20
import json
import shutil

__author__ = u'王健'

newapkfiles = 'newapkfiles'

user_agent = "image uploader"
default_message = "Image $current of $total"

# urlbase = 'http://192.168.101.18:8000/mogu'
urlbase = 'http://openfire.mmggoomm.com/mogu'
uploadurl = '%s/PluginUploadScript' % urlbase
uploadurlcheck = '%s/PluginUploadNeedScript' % urlbase

iconupload = '%s/PluginIconUpload' % urlbase
imageupload = '%s/PluginImageUpload' % urlbase
apkupload = '%s/PluginApkUpload' % urlbase
# uploadurl2 = 'http://mogu-mmggoo.appsp0t.com/PluginUploadApkScript'

import logging
import os
from os.path import abspath, isabs, isdir, isfile, join
import random
import string
import sys
import mimetypes
import urllib2
import httplib
import time
import re


def random_string(length):
    return ''.join(random.choice(string.letters) for ii in range(length + 1))


class Apk():
    def setFileName(self, file):
        self.f = open(file, 'rb')
        self.num = 0

    def setB(self, bo):
        self.b = bo

    def read(self, n):
        if self.num == 0:
            self.num += 1
            return self.b

        return self.f.read(n)


def encode_multipart_data2(data, files):
    boundary = random_string(30)

    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_field(field_name):
        return ('--' + boundary,
                'Content-Disposition: form-data; name="%s"' % field_name,
                '', str(data[field_name]))

    def encode_file(field_name):
        filename = files[field_name]
        return ('--' + boundary,
                'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename.split('/')[-1]),
                'Content-Type: %s' % get_content_type(filename),
                '', '')


    lines = []
    for name in data:
        lines.extend(encode_field(name))
    for name in files:
        lines.extend(encode_file(name))
    lines.extend(('--%s--' % boundary, ''))
    body = '\r\n'.join(lines)

    headers = {'content-type': 'multipart/form-data; boundary=' + boundary, 'User-agent': 'Mozilla/5.0',
               'content-length': str(len(open(files['file'], 'rb').read()) + len(body))}
    apk = Apk()
    apk.setB(body)
    apk.setFileName(files['file'])
    return apk, headers


def encode_multipart_data(data, files):
    boundary = random_string(30)

    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_field(field_name):
        return ('--' + boundary,
                'Content-Disposition: form-data; name="%s"' % field_name,
                '', str(data[field_name]))

    def encode_file(field_name):
        filename = files[field_name]
        return ('--' + boundary,
                'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename.split('/')[-1]),
                'Content-Type: %s' % get_content_type(filename),
                '', open(filename, 'rb').read())

    lines = []
    for name in data:
        lines.extend(encode_field(name))
    for name in files:
        lines.extend(encode_file(name))
    lines.extend(('--%s--' % boundary, ''))
    body = '\r\n'.join(lines)

    headers = {'content-type': 'multipart/form-data; boundary=' + boundary,
               'DNT': '1',
               'Connection': 'keep-alive',
               'Accept-Encoding': ' deflate',
               'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
               'content-length': str(len(body))}

    return body, headers


def send_post(url, data):
    req = urllib2.Request(url)
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    connection = httplib.HTTPConnection(req.get_host())
    connection.request('POST', req.get_selector(),
                       *encode_multipart_data(data, {}))
    response = connection.getresponse()

    return response.read()


def send_post2(url, data, files):
    req = urllib2.Request(url)
    req.add_header('User-agent', 'Mozilla/5.0')
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    connection = httplib.HTTPConnection(req.get_host())
    connection.request('POST', req.get_selector(),
                       *encode_multipart_data(data, files))
    response = connection.getresponse()

    return response.read()
    # logging.debug('response = %s', response.read())
    # logging.debug('Code: %s %s', response.status, response.reason)


def make_upload_file(server, thread, delay=15, message=None,
                     username=None, email=None, password=None):
    delay = max(int(delay or '0'), 15)

    def upload_file(path, current, total):
        assert isabs(path)
        assert isfile(path)

        logging.debug('Uploading %r to %r', path, server)
        message_template = string.Template(message or default_message)

        data = {'MAX_FILE_SIZE': '3145728',
                'sub': '',
                'mode': 'regist',
                'com': message_template.safe_substitute(current=current, total=total),
                'resto': thread,
                'name': username or '',
                'email': email or '',
                'pwd': password or random_string(20), }
        files = {'upfile': path}

        send_post(server, data, files)

        logging.info('Uploaded %r', path)
        rand_delay = random.randint(delay, delay + 5)
        logging.debug('Sleeping for %.2f seconds------------------------------\n\n', rand_delay)
        time.sleep(rand_delay)

    return upload_file


def upload_directory(path, upload_file):
    assert isabs(path)
    assert isdir(path)

    matching_filenames = []
    file_matcher = re.compile(r'\.(?:jpe?g|gif|png)$', re.IGNORECASE)

    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            file_path = join(dirpath, name)
            logging.debug('Testing file_path %r', file_path)
            if file_matcher.search(file_path):
                matching_filenames.append(file_path)
            else:
                logging.info('Ignoring non-image file %r', path)

    total_count = len(matching_filenames)
    for index, file_path in enumerate(matching_filenames):
        upload_file(file_path, index + 1, total_count)


def run_upload(options, paths):
    upload_file = make_upload_file(**options)

    for arg in paths:
        path = abspath(arg)
        if isdir(path):
            upload_directory(path, upload_file)
        elif isfile(path):
            upload_file(path)
        else:
            logging.error('No such path: %r' % path)

    logging.info('Done!')


def uploadApkOnly():
    # from poster.encode import multipart_encode
    # from poster.streaminghttp import register_openers
    # import urllib2
    i = 1
    for dirname in os.listdir(newapkfiles):
        try:
            apkdirlist = os.listdir('%s/%s' % (newapkfiles, dirname))
        except:
            continue
        print 'no. %s' % i
        i += 1
        data = {'appcode': 'com.mfp.frozen.playgame.disney'}
        files = {'file': '4.jpg'}
        apkdir = ''
        num = 1
        # for filename in apkdirlist:
        #     if filename[-4:] == '.apk':
        #         apkdir = '%s/%s/%s'%(newapkfiles, dirname, filename)
        #     if filename.find('package.txt')>=0:
        #         data['appcode']=open('%s/%s/%s'%(newapkfiles, dirname, filename),'r').read()


        result = send_post(uploadurl, data, {})
        r = json.loads(result)
        # register_openers()
        if r.get('status', 0) == 200:
            #datagen, headers = multipart_encode({"file": open(apkdir, "rb")})
            #request = urllib2.Request(str(r.get('upload_url')), datagen, headers)
            #print urllib2.urlopen(request).read()
            #print send_post('http://mogu-mmggoo.appspot.com/_ah/upload/?id=6416702615060480&pluginid=4896155343257600/AMmfu6b-snciTp0aUc_hjzq0zjfDzUj2d1JCVMzfM4CAABLjMZZu36kGMSN7LMK2Rg-i1ql7_tF5Qos0RAidXR_JnrGoyQfdkxIIFxK58LwccI_UhAzyUHUHac1cImaH3gJp0QtNcaqjU3mmtmVIqm9JZsSEt-ca7oOEOz7qGIc6GoIomHCrzEA/ALBNUaYAAAAAUx3QZzF6Yb38tzMLRxWvq22S3Sc0sHUF/',{},{'file': apkdir})
            print send_post(str(r.get('upload_url')), {}, files)
            print 'success:%s' % dirname

        else:
            print '%s:%s' % (r.get('status'), dirname)


def uploadApks(dirname):
    l = []
    successlist = []

    errorlist = []
    # for d in os.listdir(newapkfiles):
    #     l.append(d)
    # for dirname in l:
    # dirname = dirname.decode('gbk')
    print '开始上传：%s ' % dirname
    try:
        apkdirlist = os.listdir('%s/%s' % (newapkfiles, dirname))
    except:
        return

    data = {}
    # files = {}
    iconfiles = None
    imagefiles = []
    apkdir = ''
    num = 1
    for filename in apkdirlist:
        if filename[-4:] == '.apk':
            apkdir = '%s/%s/%s' % (newapkfiles, dirname, filename)
        if filename.find('.jpg') > 0:
            imagefiles.append('%s/%s/%s' % (newapkfiles, dirname, filename))
            num += 1
        if filename.find('.png') > 0:
            iconfiles = '%s/%s/%s' % (newapkfiles, dirname, filename)
        # if filename.find('versioncode.txt')>=0:
        #     data['versioncode']=open('%s/%s/%s'%(newapkfiles, dirname, filename),'r').read()
        # if filename.find('versionnum.txt')>=0:
        #     data['versionnum']=open('%s/%s/%s'%(newapkfiles, dirname, filename),'r').read()
        if filename.find('package.txt') >= 0:
            data['appcode'] = open('%s/%s/%s' % (newapkfiles, dirname, filename), 'r').read()
        if filename.find('desc.txt') >= 0:
            data['desc'] = open('%s/%s/%s' % (newapkfiles, dirname, filename), 'r').read()
            # data['updateDesc']=''
        if filename.find('codenum.txt') >= 0:
            data['code'] = 'a4-s' + file('%s/%s/%s' % (newapkfiles, dirname, filename), 'r').read()
        if filename.find('appname.txt') >= 0:
            data['name'] = file('%s/%s/%s' % (newapkfiles, dirname, filename), 'r').read()

    try:
        data['imagenum'] = len(imagefiles)
        resultcheck = send_post(uploadurlcheck, data)
        rc = json.loads(resultcheck)
        rc = rc['result']

        result = send_post(uploadurl, data)
        r = json.loads(result)
        r = r['result']
        upload_apk_url = None
        if rc.has_key('upload_url') or r.has_key('upload_url'):
            upload_apk_url = '%s?pluginid=%s' % (apkupload, r.get('id'))

        if upload_apk_url:
            try:
                upload_img(dirname, str(upload_apk_url), {'file': apkdir})
            except Exception, e:
                print '上传失败(apk)：%s' % dirname
                # raise e

        upload_image_url = []
        if rc.has_key('upload_image_url') or r.has_key('upload_image_url'):
            upload_image_url = '%s?pluginid=%s' % (imageupload, r.get('id'))
        try:
            if upload_image_url:
                for k, u in enumerate(imagefiles):
                    upload_img(dirname, str(upload_image_url), {'file': u})
        except Exception, e:
            print '上传失败(image)：%s' % dirname
            # raise e

        upload_icon_url = None
        if rc.has_key('upload_icon_url') or r.has_key('upload_icon_url'):
            upload_icon_url = '%s?pluginid=%s' % (iconupload, r.get('id'))
        if upload_icon_url:
            try:
                upload_img(dirname, str(upload_icon_url), {'file': iconfiles})
            except Exception, e:
                print '上传失败(icon)：%s' % dirname
                # raise e
        print '上传完成：%s' % dirname
    except Exception, e:
        pass

        # shutil.rmtree('%s/%s' % (newapkfiles, dirname))


#.replace("mogu-mmggoo.appspot.com","mogu-mmggoo.appsp0t.com")

def upload_img(dirname, url, iconfiles):
    iconresult = send_post2(url, {}, iconfiles)
    if iconresult:
        iconr = json.loads(iconresult)
        if iconr.get('status_code', 0) == 200:
            print 'success:%s' % dirname
    else:
        print 'error:' % dirname


if __name__ == '__main__':
    #uploadApks()
    uploadApkOnly()
    #printl()