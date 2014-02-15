#coding=utf-8
#author:u'王健'
#Date: 14-2-15
#Time: 下午2:15
__author__ = u'王健'

import os
import shutil
import xml.dom.minidom

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

def Indent(dom, node, indent = 0):
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

def apkfile(apkname):
    return '%s/%s'%(apkfiles,apkname)


def cacheapkfile(apkname):
    return '%s/%s'%(cachefiles,apkname.replace('.apk','').replace('.','_'))

def newapkfile(apkname):
    return '%s/%s'%(newapkfiles,apkname)


password = raw_input(u'输入签名密码')
code = 'a4-s'
codenum = 1010

apkfiles = 'apkfiles'
newapkfiles = 'newapkfiles'
cachefiles = 'cachefiles'

apklist = []
if os.path.exists(cachefiles):
    shutil.rmtree(cachefiles)
os.mkdir(cachefiles)
if os.path.exists(newapkfiles):
    shutil.rmtree(newapkfiles)
os.mkdir(newapkfiles)
for dirname in os.listdir('apkfiles'):
    if dirname.find('.apk')<0:
        continue
    apklist.append(dirname)
    print dirname
    cmdExtract = r'java -jar lib/apktool.jar  d -f -s %s %s'% (apkfile(dirname),cacheapkfile(dirname))
    #cmdExtract = r'java -jar lib/apktool.jar  d -f -s %s %s'% (apkfile(dirname),cacheapkfile(dirname))
    os.system(cmdExtract)



    #xmlstr = []
    #for line in file('%s/AndroidManifest.xml'%newapkfile(dirname),'r'):
    #    xmlstr.append(line)
    androidManifest = xml.dom.minidom.parse('%s/AndroidManifest.xml'%cacheapkfile(dirname))
    node = androidManifest.getElementsByTagName("manifest")[0]
    package= node.getAttribute("package")
    print package
    node.setAttribute('android:sharedUserId','com.mogu3.allsharedid')

    application = androidManifest.getElementsByTagName('application')[0]
    appnameres = application.getAttribute('android:label').replace('@string/','')
    appname = ''
    stringxml = xml.dom.minidom.parse('%s/res/values/strings.xml'%cacheapkfile(dirname))

    for s in stringxml.getElementsByTagName('string'):
        if s.getAttribute('name') == appnameres:
            appname = s.childNodes[0].nodeValue
            print appname
    if not appname:
        continue
    if os.path.exists(newapkfile(appname)):
        shutil.rmtree(newapkfile(appname))
    os.mkdir(newapkfile(appname))

    iconres = application.getAttribute('android:icon').replace('@drawable/','')
    iconsrc0 = '%s/res/drawable/%s.png'%(cacheapkfile(dirname),iconres)
    iconsrc1 = '%s/res/drawable-hdpi/%s.png'%(cacheapkfile(dirname),iconres)
    iconsrc2 = '%s/res/drawable-xhdpi/%s.png'%(cacheapkfile(dirname),iconres)
    iconsrc3 = '%s/res/drawable-xxhdpi/%s.png'%(cacheapkfile(dirname),iconres)
    if os.path.exists(iconsrc0):
        shutil.copyfile(iconsrc0,'%s/%s.png'%(newapkfile(appname),iconres))
    elif os.path.exists(iconsrc1):
        shutil.copyfile(iconsrc1,'%s/%s.png'%(newapkfile(appname),iconres))
    elif os.path.exists(iconsrc2):
        shutil.copyfile(iconsrc2,'%s/%s.png'%(newapkfile(appname),iconres))
    elif os.path.exists(iconsrc3):
        shutil.copyfile(iconsrc3,'%s/%s.png'%(newapkfile(appname),iconres))




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
            if mainclass[0]=='.':
                mainclass = '%s%s'%(package,mainclass)

            node.setAttribute('android:name',mainclass)
            categorylist = node.parentNode.getElementsByTagName('category')

            for categorynode in categorylist:
                if categorynode.getAttribute('android:name') =="android.intent.category.LAUNCHER":
                    categorynode.setAttribute('android:name','android.intent.category.DEFAULT')

    print mainclass
    codenum+=1
    pluginfile = file('%s/assets/plugin.xml'%cacheapkfile(dirname),'w')
    pluginfile.write((pluginxml%(mainclass,appname,'%s%s'%(code,codenum))).encode('utf-8'))
    pluginfile.close()

    f=file('%s/AndroidManifest.xml'%cacheapkfile(dirname),'w')
    import codecs
    androidManifestcopy = androidManifest.cloneNode(True)
    Indent(androidManifestcopy,androidManifestcopy.documentElement)
    write = codecs.lookup('utf-8')[3](f)
    androidManifestcopy.writexml(write,encoding='utf-8')
    write.close()

    unsignApk = r'%s/%s.apk'% (cachefiles, dirname.replace('.apk','').replace('.','_'))
    cmdPack = r'java -jar lib/apktool.jar b -f %s %s'% (cacheapkfile(dirname),unsignApk)
    os.system(cmdPack)

    cmd_sign = r'jarsigner -verbose -keystore lib/MoGu3 -storepass %s -signedjar %s %s tianxingjian'% (password,'%s/%s'%(newapkfile(appname),dirname),unsignApk)
    os.system(cmd_sign.encode('utf-8'))


if os.path.exists(cachefiles):
    shutil.rmtree(cachefiles)

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
