#!/usr/bin/env python
# -*- coding:utf8 -*-


mimes = {
    'hqx'  :  'application/mac-binhex40',
    'cpt'  :  'application/mac-compactpro',
    'csv'  :  'text/x-comma-separated-values',
    'bin'  :  'application/macbinary',
    'dms'  :  'application/octet-stream',
    'lha'  :  'application/octet-stream',
    'lzh'  :  'application/octet-stream',
    'exe'  :  'application/x-msdownload',
    'class':  'application/octet-stream',
    'psd'  :  'application/x-photoshop',
    'so'   :  'application/octet-stream',
    'sea'  :  'application/octet-stream',
    'dll'  :  'application/octet-stream',
    'oda'  :  'application/oda',
    'pdf'  :  'application/pdf',
    'ai'   :  'application/postscript',
    'eps'  :  'application/postscript',
    'ps'   :  'application/postscript',
    'smi'  :  'application/smil',
    'smil' :  'application/smil',
    'mif'  :  'application/vnd.mif',
    'xls'  :  'application/excel',
    'ppt'  :  'application/powerpoint',
    'wbxml':  'application/wbxml',
    'wmlc' :  'application/wmlc',
    'dcr'  :  'application/x-director',
    'dir'  :  'application/x-director',
    'dxr'  :  'application/x-director',
    'dvi'  :  'application/x-dvi',
    'gtar' :  'application/x-gtar',
    'gz'   :  'application/x-gzip',
    'php'  :  'application/x-httpd-php',
    'php4' :  'application/x-httpd-php',
    'php3' :  'application/x-httpd-php',
    'phtml':  'application/x-httpd-php',
    'phps' :  'application/x-httpd-php-source',
    'js'   :  'application/x-javascript',
    'swf'  :  'application/x-shockwave-flash',
    'sit'  :  'application/x-stuffit',
    'tar'  :  'application/x-tar',
    'tgz'  :  'application/x-tar',
    'xhtml':  'application/xhtml+xml',
    'xht'  :  'application/xhtml+xml',
    'zip'  :  'application/x-zip',
    'mid'  :  'audio/midi',
    'midi' :  'audio/midi',
    'mpga' :  'audio/mpeg',
    'mp2'  :  'audio/mpeg',
    'mp3'  :  'audio/mp3',
    'aif'  :  'audio/x-aiff',
    'aiff' :  'audio/x-aiff',
    'aifc' :  'audio/x-aiff',
    'ram'  :  'audio/x-pn-realaudio',
    'rm'   :  'audio/x-pn-realaudio',
    'rpm'  :  'audio/x-pn-realaudio-plugin',
    'ra'   :  'audio/x-realaudio',
    'rv'   :  'video/vnd.rn-realvideo',
    'wav'  :  'audio/wav',
    'bmp'  :  'image/bmp', 
    'gif'  :  'image/gif',
    'jpeg' :  'image/jpeg',
    'jpg'  :  'image/jpeg',
    'jpe'  :  'image/jpeg',
    'png'  :  'image/png' ,
    'tiff' :  'image/tiff',
    'tif'  :  'image/tiff',
    'css'  :  'text/css',
    'html' :  'text/html',
    'htm'  :  'text/html',
    'shtml':  'text/html',
    'txt'  :  'text/plain',
    'text' :  'text/plain',
    'log'  :  'text/plain',
    'rtx'  :  'text/richtext',
    'rtf'  :  'text/rtf',
    'xml'  :  'text/xml',
    'xsl'  :  'text/xml',
    'mpeg' :  'video/mpeg',
    'mpg'  :  'video/mpeg',
    'mpe'  :  'video/mpeg',
    'qt'   :  'video/quicktime',
    'mov'  :  'video/quicktime',
    'avi'  :  'video/x-msvideo',
    'movie':  'video/x-sgi-movie',
    'doc'  :  'application/msword',
    'docx' :  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xlsx' :  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'word' :  'application/msword',
    'xl'   :  'application/excel',
    'eml'  :  'message/rfc822',
    'json' :  'application/json'
}
import os

class CI_Static(object):

    def __init__(self, **kwargs):
        super(CI_Static, self).__init__()
        self.application_path= kwargs['application_path']
        self.app = kwargs['app']
        self.static_path = kwargs['server']['static_dir']
    
    def accept(self,env):
        paths = [e for e in env['PATH_INFO'].split("/") if e <> ""]
        ##防止读取上层目录
        if ".." in paths:
            return False
        if paths[0] == self.static_path:
            path = "%s/%s"  % ( self.application_path , "/".join(paths) )
            ##如果文件存在则跑静态路由
            if os.path.exists(path):
                return True

        return False

    def route(self,env):
        paths = [e for e in env['PATH_INFO'].split("/") if e <> ""]
        path = "./%s"  %"/".join(paths)
        filename = paths[-1]
        extname = filename.split(".")[-1]
        mime = mimes.get(extname,"text/html")
        self.app.set_header("Content-type",mime)
        content = b""
        with open(path) as fp:
            content = fp.read()
        return "200 OK",content

        

