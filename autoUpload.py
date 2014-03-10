#coding=utf-8
#author:u'王健'
#Date: 14-3-9
#Time: 下午3:20
import json

__author__ = u'王健'

newapkfiles = 'newapkfiles'

user_agent = "image uploader"
default_message = "Image $current of $total"

uploadurl = 'http://localhost:8180/PluginUploadScript'

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
               'content-length': str(len(body))}

    return body, headers


def send_post(url, data, files):
    req = urllib2.Request(url)
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


def uploadApks():
    for dirname in os.listdir(newapkfiles):
        try:
            apkdirlist = os.listdir('%s/%s' % (newapkfiles, dirname))
        except:
            continue
        data = {'name':dirname.decode('gbk').encode('utf-8')}
        files = {}
        apkdir = ''
        num = 1
        for filename in apkdirlist:
            if filename[-4:] == '.apk':
                apkdir = '%s/%s/%s'%(newapkfiles, dirname, filename)
            if filename.find('.jpg')>0:
                files['image%s'%num] =  '%s/%s/%s'%(newapkfiles, dirname, filename)
                num+=1
            if filename.find('.png')>0:
                files['icon'] = '%s/%s/%s'%(newapkfiles, dirname, filename)
            if filename.find('versioncode.txt')>=0:
                data['versioncode']=open('%s/%s/%s'%(newapkfiles, dirname.decode('gbk'), filename),'r').read()
            if filename.find('versionnum.txt')>=0:
                data['versionnum']=open('%s/%s/%s'%(newapkfiles, dirname.decode('gbk'), filename),'r').read()
            if filename.find('package.txt')>=0:
                data['appcode']=open('%s/%s/%s'%(newapkfiles, dirname.decode('gbk'), filename),'r').read()
            if filename.find('desc.txt')>=0:
                data['desc']=open('%s/%s/%s'%(newapkfiles, dirname.decode('gbk'), filename),'r').read()
                data['updateDesc']=''
            if filename.find('codenum.txt')>=0:
                data['code']=file('%s/%s/%s'%(newapkfiles, dirname.decode('gbk'), filename),'r').read()

        result = send_post(uploadurl, data, files)
        r = json.loads(result)
        if r.get('status', 0) == 200:
            send_post(str(r.get('upload_url')),{},{'file': apkdir})

if __name__=='__main__':
    uploadApks()