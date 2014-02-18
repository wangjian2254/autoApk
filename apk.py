#coding=utf-8
#author:u'王健'
#Date: 14-2-15
#Time: 下午2:15
#import urllib.request
import Queue
import threading
import urllib
import urllib2, HTMLParser

__author__ = u'王健'

import os
import shutil
import xml.dom.minidom
import subprocess

pluginxml = u'''<?xml version="1.0" encoding="UTF-8"?>
<plugin-features>
    <version>1</version>
	<intent action="%s" key="main">
	    %s
	</intent>

	<code>%s</code>
	<type>game</type>

</plugin-features>
'''


def Indent(dom, node, indent=0):
    # Copy child list because it will change soon
    children = node.childNodes[:]
    # Main node doesn't need to be indented
    if indent:
        text = dom.createTextNode('\n' + '\t' * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        # Append newline after last child, except for text nodes
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode('\n' + '\t' * indent)
            node.appendChild(text)
        # Indent children which are elements
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                Indent(dom, n, indent + 1)


#def readChannelfile(filename):
#    f = file(filename)
#    while True:
#        line = f.readline().strip('\n')
#        if len(line) == 0:
#            break
#        else:
#            channelList.append(line);
#    f.close()
#
#def backUpManifest():
#    if os.path.exists('./AndroidManifest.xml'):
#        os.remove('./AndroidManifest.xml')
#    manifestPath = './temp/AndroidManifest.xml'
#    shutil.copyfile(manifestPath, './AndroidManifest.xml')
#
#def modifyChannel(value):
#    tempXML = ''
#    f = file('./AndroidManifest.xml')
#    for line in f:
#        if line.find('channel_value') > 0:
#            line = line.replace('channel_value', value)
#        tempXML += line
#    f.close()
#
#    output = open('./temp/AndroidManifest.xml', 'w')
#    output.write(tempXML)
#    output.close()
#
#    unsignApk = r'./bin/%s_%s_unsigned.apk'% (easyName, value)
#    cmdPack = r'java -jar apktool.jar b temp %s'% (unsignApk)
#    os.system(cmdPack)
#
#    unsignedjar = r'./bin/%s_%s_unsigned.apk'% (easyName, value)
#    signed_unalignedjar = r'./bin/%s_%s_signed_unaligned.apk'% (easyName, value)
#    signed_alignedjar = r'./bin/%s_%s.apk'% (easyName, value)
#    cmd_sign = r'jarsigner -verbose -keystore %s -storepass %s -signedjar %s %s %s'% (keystore, storepass, signed_unalignedjar, unsignedjar, alianame)
#    cmd_align = r'zipalign -v 4 %s %s' % (signed_unalignedjar, signed_alignedjar)
#    os.system(cmd_sign)
#    os.remove(unsignedjar)
#    os.system(cmd_align)
#    os.remove(signed_unalignedjar)

def apkfile(apkdir, apkname):
    return '%s/%s/%s' % (apkfiles, apkdir, apkname)


def cacheapkfile(apkname):
    return '%s/%s' % (cachefiles, apkname.replace('.apk', '').replace('.', '_'))


def newapkfile(apkname):
    return '%s/%s' % (newapkfiles, apkname)


def autoApk():
    global success
    code = 'a4-s'
    codenum = 1010

    apklist = []
    if os.path.exists(cachefiles):
        shutil.rmtree(cachefiles)
    os.mkdir(cachefiles)
    if os.path.exists(newapkfiles):
        shutil.rmtree(newapkfiles)
    os.mkdir(newapkfiles)
    for apkdir in os.listdir(apkfiles):
        #if '.DS_Store' == apkdir:
        #    continue
        try:
            apkdirlist = os.listdir('%s/%s' % (apkfiles, apkdir))
        except:
            continue
        for dirname in apkdirlist:
            if dirname[-4:] == '.apk':
                apkdirlist.remove(dirname)
                apkdirlist.insert(0, dirname)
        if apkdirlist[0][-4:] != '.apk':
            continue
        appname = ''
        for dirname in apkdirlist:
            if dirname[-4:] != '.apk':
                shutil.copyfile(apkfile(apkdir, dirname), '%s/%s' % (newapkfile(appname), dirname))
                continue

            apklist.append(dirname)
            print dirname
            cmdExtract = r'java -jar lib/apktool.jar  d -f -s %s %s' % (apkfile(apkdir, dirname), cacheapkfile(dirname))
            #cmdExtract = r'java -jar lib/apktool.jar  d -f -s %s %s'% (apkfile(dirname),cacheapkfile(dirname))
            #os.system(cmdExtract)
            p = subprocess.Popen(cmdExtract, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            linelist = []
            for line in p.stdout.readlines():
                linelist.append(line)
            if 'Exception' in ''.join(linelist):
                print '失败了:%s' % apkdir
                for line in linelist:
                    print line
                break

            #xmlstr = []
            #for line in file('%s/AndroidManifest.xml'%newapkfile(dirname),'r'):
            #    xmlstr.append(line)
            androidManifest = xml.dom.minidom.parse('%s/AndroidManifest.xml' % cacheapkfile(dirname))
            node = androidManifest.getElementsByTagName("manifest")[0]
            package = node.getAttribute("package")
            print package
            node.setAttribute('android:sharedUserId', 'com.mogu3.allsharedid')

            application = androidManifest.getElementsByTagName('application')[0]
            appnameres = application.getAttribute('android:label').replace('@string/', '')

            if not os.path.exists('%s/res/values/strings.xml' % cacheapkfile(dirname)):
                break


            stringxml = xml.dom.minidom.parse('%s/res/values/strings.xml' % cacheapkfile(dirname))

            for s in stringxml.getElementsByTagName('string'):
                if s.getAttribute('name') == appnameres:
                    appname = s.childNodes[0].nodeValue
                    print appname
            if not appname:
                break
            if os.path.exists(newapkfile(appname)):
                shutil.rmtree(newapkfile(appname))
            os.mkdir(newapkfile(appname))

            iconres = application.getAttribute('android:icon').replace('@drawable/', '')
            iconsrc0 = '%s/res/drawable/%s.png' % (cacheapkfile(dirname), iconres)
            iconsrc1 = '%s/res/drawable-hdpi/%s.png' % (cacheapkfile(dirname), iconres)
            iconsrc2 = '%s/res/drawable-xhdpi/%s.png' % (cacheapkfile(dirname), iconres)
            iconsrc3 = '%s/res/drawable-xxhdpi/%s.png' % (cacheapkfile(dirname), iconres)
            if os.path.exists(iconsrc0):
                shutil.copyfile(iconsrc0, '%s/%s.png' % (newapkfile(appname), iconres))
            elif os.path.exists(iconsrc1):
                shutil.copyfile(iconsrc1, '%s/%s.png' % (newapkfile(appname), iconres))
            elif os.path.exists(iconsrc2):
                shutil.copyfile(iconsrc2, '%s/%s.png' % (newapkfile(appname), iconres))
            elif os.path.exists(iconsrc3):
                shutil.copyfile(iconsrc3, '%s/%s.png' % (newapkfile(appname), iconres))

            usersdk = androidManifest.getElementsByTagName('uses-sdk')
            if len(usersdk):
                node = usersdk[0]
                sdkversion = node.getAttribute('minSdkVersion')
            else:
                sdkversion = u'所有版本'
            print sdkversion
            activity = androidManifest.getElementsByTagName('action')
            mainclass = ''
            for node in activity:
                if node.getAttribute('android:name') == 'android.intent.action.MAIN':
                    mainclass = node.parentNode.parentNode.getAttribute('android:name')
                    if mainclass[0] == '.':
                        mainclass = '%s%s' % (package, mainclass)

                    node.setAttribute('android:name', mainclass)
                    categorylist = node.parentNode.getElementsByTagName('category')

                    for categorynode in categorylist:
                        if categorynode.getAttribute('android:name') == "android.intent.category.LAUNCHER":
                            categorynode.setAttribute('android:name', 'android.intent.category.DEFAULT')

            print mainclass
            codenum += 1
            pluginfile = file('%s/assets/plugin.xml' % cacheapkfile(dirname), 'w')
            pluginfile.write((pluginxml % (mainclass, appname, '%s%s' % (code, codenum))).encode('utf-8'))
            pluginfile.close()

            f = file('%s/AndroidManifest.xml' % cacheapkfile(dirname), 'w')
            import codecs

            androidManifestcopy = androidManifest.cloneNode(True)
            Indent(androidManifestcopy, androidManifestcopy.documentElement)
            write = codecs.lookup('utf-8')[3](f)
            androidManifestcopy.writexml(write, encoding='utf-8')
            write.close()

            unsignApk = r'%s/%s_unsign.apk' % (cachefiles, dirname.replace('.apk', '').replace('.', '_'))
            cmdPack = r'java -jar lib/apktool.jar b -f %s %s' % (cacheapkfile(dirname), unsignApk)
            # os.system(cmdPack)
            p = subprocess.Popen(cmdPack, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            linelist = []
            for line in p.stdout.readlines():
                linelist.append(line)
            if 'Exception' in ''.join(linelist):
                print '失败了:%s' % apkdir
                for line in linelist:
                    print line



            signApk = unsignApk.replace('_unsign', '')
            cmd_sign = r"jarsigner -verbose -keystore lib/MoGu3 -storepass %s -signedjar %s %s tianxingjian" % (
                password, signApk, unsignApk)
            # os.system(cmd_sign.encode('utf-8'))
            p = subprocess.Popen(cmd_sign.encode('utf-8'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            linelist = []
            for line in p.stdout.readlines():
                linelist.append(line)
            if os.path.exists(signApk):
                shutil.copyfile(signApk, signApk.replace(cachefiles, '%s/%s' % (newapkfiles, appname)))
                success += 1
            else:
                shutil.rmtree(newapkfile(appname))
                for line in linelist:
                    print line
                break

    if os.path.exists(cachefiles):
        shutil.rmtree(cachefiles)


class ShowStructure(HTMLParser.HTMLParser):
    def setlist(self, l):
        self.alist = l
        self.start = False

    def handle_starttag(self, tag, attrs):
        if tag == 'ul':
            for att, val in attrs:
                if att == 'id' and val == 'iconList':
                    self.start = True
        if self.start and tag == 'a':
            for att, val in attrs:
                if att == 'href' and val not in self.alist and val.find('zhushou360://') == -1:
                    self.alist.append(val)
                    #self.alist.append(tag)

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.start = False
            #self.alist.pop()

    def handle_data(self, data):
        pass
        #if data.strip():
        #    for tag in self.alist:
        #        sys.stdout.write('/'+tag)
        #    sys.stdout.write(' >> %s/n' % data[:40].strip())


class ApkPage(HTMLParser.HTMLParser):
    def setlist(self):
        self.infodict = {'apkinfo': '', 'imglist': []}
        self.info = False
        self.img = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for att, val in attrs:
                if att == 'class' and val == 'breif':
                    self.info = True
                if att == 'class' and val == 'overview':
                    self.img = True
        if self.img and tag == 'img':
            for att, val in attrs:
                if att == 'src' and val not in self.infodict['imglist']:
                    self.infodict['imglist'].append(val)
                    #self.alist.append(tag)

    def handle_endtag(self, tag):
        if self.info and tag == 'div':
            self.info = False
        if self.img and tag == 'div':
            self.img = False
            #self.alist.pop()

    def handle_data(self, data):
        if self.info:
            self.infodict['apkinfo'] = data
            #if data.strip():
            #    for tag in self.alist:
            #        sys.stdout.write('/'+tag)
            #    sys.stdout.write(' >> %s/n' % data[:40].strip())

class DownloadApkAndImage(threading.Thread):
    def __init__(self,q):
        threading.Thread.__init__(self)
        self.q=q
    def run(self):
        global num
        url=None
        while True:
            queueLock = threading.Lock()
            if self.q.empty():
                queueLock.acquire()
                break
            else:
                num += 1
                url = self.q.get()
                print '第%s 个开始'%(num)
            html = urllib2.urlopen('%s%s' % (urlbase, url)).read()
            scriptend = html.find('</script>')
            apkstart = html[:scriptend].find("'downurl':")
            apkend = html[apkstart:scriptend].find("'mkid'") + apkstart
            apkurl = html[apkstart + 10:apkend].split("'")[1]
            print apkurl


            dirname = url.split('/')[-1]
            filename = apkurl.split('/')[-1]
            if os.path.exists('%s/%s'%(apkfiles,dirname)):
                shutil.rmtree('%s/%s'%(apkfiles,dirname))
            os.mkdir('%s/%s'%(apkfiles,dirname))
            urllib.urlretrieve(apkurl,"%s/%s/%s"%(apkfiles,dirname,filename))

            linelist = []
            for line in html.split('\r\n'):
                linelist.append(line.decode('utf-8'))
            apkinfo = ApkPage()
            apkinfo.setlist()
            apkinfo.feed(''.join(linelist))
            with open("%s/%s/desc.txt" % (apkfiles, dirname), "w") as code:
                code.write(apkinfo.infodict['apkinfo'].encode('utf-8').replace('\n', ''))
            with open("%s/%s/address.txt" % (apkfiles, dirname), "w") as code:
                code.write(url)
            for i, imgurl in enumerate(apkinfo.infodict['imglist']):
                print imgurl
                f = urllib2.urlopen(imgurl)
                data = f.read()
                filename = imgurl.split('.')[-1]
                with open("%s/%s/%s.%s" % (apkfiles, dirname, i, filename), "wb") as code:
                    code.write(data)


def downloadApk():


    urlstr = '''
    http://zhushou.360.cn/list/index/cid/2
    http://zhushou.360.cn/list/index/cid/2?page=2
    http://zhushou.360.cn/list/index/cid/2?page=3
    http://zhushou.360.cn/list/index/cid/2?page=4
    http://zhushou.360.cn/list/index/cid/2?page=5
    '''
    apkurllist = []
    for url in urlstr.split()[:1]:

        html = urllib2.urlopen(url).read()
        s = ShowStructure()
        s.setlist(apkurllist)
        s.feed(html)
    queueLock = threading.Lock()
    workQueue = Queue.Queue(len(apkurllist))
    queueLock.acquire()
    for url in apkurllist:
        workQueue.put(url)
    queueLock.release()
    threads=[]
    for i in range(10):
        thread=DownloadApkAndImage(workQueue)
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()

urlbase = 'http://zhushou.360.cn'
apkfiles = 'apkfiles'
newapkfiles = 'newapkfiles'
cachefiles = 'cachefiles'
password = raw_input('输入签名密码:\n')

num = 49
success = 0



print '开始下载'
# downloadApk()
print '下载完成，下载 ：%s'%num
print '开始破解'
autoApk()
print '破解完成'
print '下载：%s 个，成功破解：%s 个'%(num,success)

#
#apkName = 'ApkTest.apk'
#easyName = apkName.split('.apk')[0]
#keystore='./keystore/ApkTest.keystore'
#storepass='123456'
#alianame='ApkTest.keystore'
#
#output_apk_dir="./bin"
#if os.path.exists(output_apk_dir):
#    shutil.rmtree(output_apk_dir)
#
#readChannelfile('./channel')
#print '-------------------- your channel values --------------------'
#print 'channel list: ', channelList
#cmdExtract = r'java -jar apktool.jar  d -f -s %s temp'% (apkName)
#os.system(cmdExtract)
#
#backUpManifest()
#for channel in channelList:
#    modifyChannel(channel)
#
#if os.path.exists('./temp'):
#    shutil.rmtree('./temp')
#if os.path.exists('./AndroidManifest.xml'):
#    os.remove('./AndroidManifest.xml')
#print '-------------------- Done --------------------'
