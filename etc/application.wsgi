import os
import sys

import cgi, re, os, posixpath, mimetypes
from cgi import parse_qs
#from mako.lookup import TemplateLookup
#from mako import exceptions
#import memcache
import Cookie
import cgi, hashlib
import random, datetime, json
import urllib2
import io

from urllib import quote
#import memcache, hashlib, random
import hashlib, random
import json
import hashlib

from mako.lookup import TemplateLookup
from mako import exceptions
from mako.template import Template


import memcache, hashlib
import cgi, re, memcache, hashlib, random
MEM_SERVER = '127.0.0.1' # Server Address
MEM_PORT = '11211' # Mem Port
MEM_TIMEOUT = 30   #60000 # Data TTL (Seconds)

mem = memcache.Client(['%s:%s' % (MEM_SERVER,MEM_PORT)])
#mem.delete(key)
#mem.get(key)
#mem.set(key,value, MEM_TIMEOUT)


PCKey = 'xp'  # identify pc: set from url first, else from cookie
UserKey ='xu' # identify user : as above
EmailKey = 'email'
PwdKey='pwd'
StayKey='stay'  # &stay=true
NeverExpired = (datetime.datetime.utcnow() + datetime.timedelta(days=300000)).strftime("%a, %d %b %Y %H:%M:%S GMT")
Expired = 'Sat, 16-Jul-2011 12:55:48 GMT'
#v_user = None
#v_Auth = {}

#head = {}
#cookieheaders = ('','')


root = '/var/NanoDev/'


def parseFullUrl(inEnv):
    url = inEnv['wsgi.url_scheme']+'://'
    if inEnv.get('HTTP_HOST'):
        url += inEnv['HTTP_HOST']
    else:
        url += inEnv['SERVER_NAME']
        if inEnv['wsgi.url_scheme'] == 'https':
            if inEnv['SERVER_PORT'] != '443':
                url += ':' + inEnv['SERVER_PORT']
        else:
            if inEnv['SERVER_PORT'] != '80':
                url += ':' + inEnv['SERVER_PORT']
    url += quote(inEnv.get('SCRIPT_NAME', ''))
    url += quote(inEnv.get('PATH_INFO', ''))
    if inEnv.get('QUERY_STRING'):
        url += '?' + inEnv['QUERY_STRING']
    return url


def getfield(f):  #convert values from cgi.Field objects to plain values.
    if isinstance(f, list):
        return [getfield(x) for x in f]
    else:
        return f.value



def parseHeader(inEnv ):
    global UserKey , PCKey,  EmailKey,  PwdKey,  StayKey
    v_out= {}
    v_out['srvname'] = inEnv.get('SERVER_NAME', '') #URL hostname# www.werbac.com?....    # parameters - http://wsgi.readthedocs.org/en/latest/definitions.html
    v_out['domain'] = inEnv.get('SERVER_NAME', '')  #.replace("www.","")
    v_out['querystring'] = inEnv.get('QUERY_STRING', '') #URL Params# ......?boots=10&socks=yes
    v_out['requestmethod'] = inEnv.get('REQUEST_METHOD', '')
    v_out['url'] = parseFullUrl(inEnv)
    v_out['parameters'] = parse_qs(v_out['querystring'])  # parse a more complex query string such as with special characters
    fieldstorage = cgi.FieldStorage(fp = inEnv['wsgi.input'],environ = inEnv,keep_blank_values = True)
    #print 'fieldstorage!!!!!!!! ====== ',type(fieldstorage)
    v_out['fieldstorage'] = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])
    v_out['url_user_hash'] = v_out['fieldstorage'].get(UserKey, None)   # urluser
    v_out['url_pc_hash'] =  v_out['fieldstorage'].get(PCKey, None)   #urlpc
    #Process Users
    v_out[EmailKey] =  v_out['fieldstorage'].get(EmailKey, None)   #urlemail
    v_out[PwdKey] =  v_out['fieldstorage'].get(PwdKey, None)    #urlpwd
    v_stay = v_out['fieldstorage'].get(StayKey, None)
    v_out[StayKey] =  True if (v_out['fieldstorage'].get(StayKey, None) is not None and  v_out['fieldstorage'][StayKey].lower() == 'true') else False #urlstay
    v_out['fieldstorageKeys'] = list(v_out['fieldstorage'].keys())
    v_out['scriptname'] = quote(inEnv.get('SCRIPT_NAME', ''))
    v_out['fulluri'] = quote(inEnv.get('SCRIPT_NAME', '')) + quote(inEnv.get('PATH_INFO', ''))   # Full URL -- needs to be build up....
    if not v_out['fulluri'] or v_out['fulluri'] in ['/','/index.html']:
        v_out['fulluri'] = '/index.html'
    else:
        v_out['fulluri'] =  re.sub(r'^/$', '/index.html', v_out['fulluri'])
        
    #uri = inEnv.get('PATH_INFO', '/')
    #uri = inEnv.get('SCRIPT_NAME', '/')
    uri = v_out['fulluri']
    if not uri or uri in ['/','/index.html']:
        print("parse uri: if : ",quote(inEnv.get('SCRIPT_NAME', '')), " ~~~~~~ ", quote(inEnv.get('PATH_INFO', ''))  ) # ----------------
        uri = '/index.html'
    else:
        uri = re.sub(r'^/$', '/index.html', uri)
        print("parse uri: else : ",quote(inEnv.get('SCRIPT_NAME', '')), " ~~~~~~ ", quote(inEnv.get('PATH_INFO', ''))  )   # -----------------
    v_out['uri'] = uri
    v_out['cookie'] = inEnv.get('HTTP_COOKIE',None)
    #----------------------
    cookie = Cookie.SimpleCookie(inEnv.get('HTTP_COOKIE',''))
    v_out['cookie_user_hash'] = cookie[UserKey].value if UserKey in cookie else None
    v_out['cookie_pc_hash'] = cookie[PCKey].value if PCKey in cookie else None
    # -- can take this out to improve perf
    c = {}   # Populate header dict with all cokies
    for key, morsel in cookie.iteritems():
        c[morsel.key] = morsel.value
    v_out['cookies'] = c
    #-------- IDU - IDP -------------------
    v_out[UserKey] = None
    if v_out['url_user_hash']:
        v_out[UserKey] = v_out['url_user_hash']
    elif v_out['cookie_user_hash']:
        v_out[UserKey] = v_out['cookie_user_hash']

    v_out[PCKey] = None
    if v_out['url_pc_hash']:
        v_out[PCKey] = v_out['url_pc_hash']
    elif v_out['cookie_pc_hash']:
        v_out[PCKey] = v_out['cookie_pc_hash']


    v_out['remoteaddr'] = inEnv.get('REMOTE_ADDR','192.168.254.452')
    return v_out

    
    
    
"""
def index(environ, start_response):
    #This function will be mounted on "/" and display a link to the hello world page.
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [ 'continue <hello/>' ] #Hello World Application This is the Hello World application: `continue <hello/>`_
           

def hello(environ, start_response):
    #Like the example above, but it uses the name specified in the URL get the name from the url if it was specified there.
    args = environ['myapp.url_args']
    if args:
        subject = escape(args[0])
    else:
        subject = 'World'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [ subject ]    #% {'subject': subject}]     #Hello %(subject)s Hello %(subject)s!''' % {'subject': subject}]
   


urls = [ (r'^$', hello),
         (r'hello/?$', hello),
         (r'hello/(.+)$', hello)
       ]
"""


    
    
def genRandomCookie(inEnv, iPCKey, exp_date=None):
    idp = hashlib.md5( 'PC_'+inEnv['remoteaddr']+str(random.random()) ).hexdigest()
    return genCookie(iPCKey, idp, inEnv['srvname'], exp_date)


def genCookie(key, value, domain, exp_date=None):
    co = Cookie.SimpleCookie()
    co[key] = value
    co[key]['httponly'] = True
    co[key]['path'] = "/"
    co[key]['domain'] = domain
    #co[key]['secure'] = True    # only over ssl
    if exp_date:
        co[key]['expires'] = exp_date
    cookout = ('Set-Cookie', co[key].OutputString())
    return cookout



def getUser_fromHashKey(key):   #was get_Hashuser
    v_user = None
    #xuser = cache.get(key)
    #if not xuser:
    #sql = 'SELECT * FROM users where idx=\''+key+'\''
    #db_user = db.select(sql,(key,))
    #cache - must put json obj in cache
    #tuser = json.loads('{}')
    
    userDB =  { 'c925e488b7e4':{'email':'bob@x.com', 'passwd':'pwd', 'hash':'c925e488b7e4','loggedin':'y'}
               ,'de93c74f680':{'email':'glen@x.com', 'passwd':'pwd','hash':'de93c74f680','loggedin':'y'}
               ,'e4459a1eae9d':{'email':'clive@x.com', 'passwd':'pwd','hash':'e4459a1eae9d','loggedin':'y'}
               ,'default':{'email':'default@default.com', 'passwd':'default','hash':'e4459a1eae9d','loggedin':'y'}
              }
    v_user = userDB.get(key, None)
    
    if v_user:
        print('getUser_fromHashKey: found user : '+v_user['email'])
        return v_user
    else:
        print('getUser_fromHashKey: couldnt find user: '+key)
        return None


def getUser_fromEmail(email,site): # was get_Emailuser
    v_user = None
    #xuser = cache.get(hashlib.md5(key).hexdigest())
    #sql='SELECT * FROM users where site IN (\'*\', \''+site+'\') and email = \''+email+'\''
    #db_user = db.select(sql)
    
    userDB =  { 'bob@x.com':{'email':'bob@x.com', 'passwd':'pwd', 'hash':'c925e488b7e4','loggedin':'y'}
               ,'glen@x.com':{'email':'glen@x.com', 'passwd':'pwd','hash':'de93c74f680','loggedin':'y'}
               ,'clive@x.com':{'email':'clive@x.com', 'passwd':'pwd','hash':'e4459a1eae9d','loggedin':'y'}
               ,'default':{'email':'default@default.com', 'passwd':'default','hash':'e4459a1eae9d','loggedin':'y'}
              }
    
    v_user = userDB.get(email, None)
    
    if v_user:
        print('getUser_fromEmail: Found USER : '+v_user['email']+'......................'+v_user['hash'])
        return v_user
    else:
        print('getUser_fromEmail: could not find user: '+email)
        return None


def authMe(head):
    #NBNBNBNBNBN:::: need to work out logic to user IDU & IDP in url if browser does not allow cookies
    #Auth/Cookie Logic: user browses to site:
    #    PC HashID = url else cookie -- if not set in either, set random one
    #    USER HashID = url else cookie  -- if set, load user(based on HashID)
    #         -- if logged in (determined from DB or....) set user as Active -- else set default profile
    #         -- if NOT logged in - expire (& Delete) Cookie for USER HashID
    #    URL logon Credentials => superceed USER HashID set anywhere else -- set/delete based on URL
    #    is Email & PWD & Stay in URL - authenticate -- if authed, set USER HashID in cookie for this session or indefinately based on stay
    #                                                -- If NOT authed, do nothing
    #Auth
    #global cookieheaders, v_user, v_Auth, head, UserKey
    #global UserKey
    cookieheaders = ('','')
    v_user = None
    v_Auth = {}
    if head[EmailKey] and head[PwdKey]:
        cookieheaders = genCookie(UserKey, '', head['srvname'], Expired)
        auth_user = getUser_fromEmail(head[EmailKey],str(head['srvname']))
        if auth_user:
            if auth_user['passwd'] == head[PwdKey]:
                v_user = auth_user
                v_Auth['login'] = 'success'; v_Auth['mesg'] = 'youre in'
                if head[StayKey]:
                    cookieheaders = genCookie(UserKey, auth_user['hash'], head['srvname'],  NeverExpired)
                else:
                    cookieheaders = genCookie(UserKey, auth_user['hash'], head['srvname'])
                print 'Auth: password match! & Stay:=', str(head[StayKey])            
            else:
                v_Auth['login'] = 'fail';  v_Auth['mesg'] = 'password mismatch'
                cookieheaders = genCookie(UserKey, '', head['srvname'], Expired)
                print 'Auth: Invalid Password!'
        else:
            print 'Auth: URL User not found!'
            v_Auth['mesg'] = 'no user found';  v_Auth['login'] = 'fail'
    else:   # if no credentials were passed in url
        v_Auth['login'] = 'fail'; v_Auth['mesg'] = 'no email/pwd credentials provided in URL'
        # Set User Profile - if idu valid & idu is logged in -- use user profile, else use default users profile
        if head[UserKey]:
            tmp_user= getUser_fromHashKey(head[UserKey])  # if user is identified by cookie/url
            if tmp_user:
                if tmp_user['loggedin'].lower() == 'y':
                    v_user = tmp_user
                # ?? else remove cookie

        if head[PCKey] is None:
            cookieheaders = genRandomCookie(head, PCKey, NeverExpired)  # if coockie not set - generate pc identification 
    #print('-------------------------------- : ',v_user)
    if v_user is None:
        v_user = getUser_fromHashKey('default')  # don't need to use db.... can just declare defualt user here
    #FS['user'] = v_user  #print 'V_USER', v_user
    head['user'] = v_user
    head['auth'] = v_Auth
    head['cookieheaders'] = cookieheaders
    return head
    
    
PageNotFound="""
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>404 Not Found</title>
</head><body>
<h1>Not Found</h1>
<p>The requested URL was not found on this server.</p>
<hr>
<address>Apache/2.4.7 Server Port 80</address>
</body></html>
"""
        
        
        
        
def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


extensions_map = mimetypes.types_map.copy()
extensions_map.update({'': 'text/html',}) # Default
def guess_type(path):
    """return a mimetype for the given path based on file extension."""
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']        
        
        
"""
HMH Pages
   - splash - frame - c1
              + with static content - c1
   - search - frame.... - c1 
              + content, - c1
              + pure dynamic content in search - d (based on params)
   - list trips
            - frame - c1
             + dynamic content - d (based on params)
   - view trip details
            - frame  - c1
             + content - d (based on params)
             
             
Note: 1. every url has a cached template
      2. dynamic content is base on parameters (but must still be fitted to cached template)

"""
        
        
def page_type(uri):    
    """return 1. Cacheable
              2. Static
                 Frame+content
              3. Content only - no Template processing ? is this ever the case -- even dynamic content needs a template             
    """
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map[''] 

#urls = [ (r'^$', hello),
#         (r'hello/?$', hello),
#         (r'hello/(.+)$', hello)
#       ] 
#-------------
#for regex, callback in urls:
#    match = re.search(regex, path)
#    if match is not None:
#        environ['myapp.url_args'] = match.groups()
#        return callback(environ, start_response)
#-------------
 
#http://www.makotemplates.org/
#http://docs.makotemplates.org/en/latest/usage.html#using-file-based-templates
def getPage(d,f, head): 
    #global head, v_user      #cookieheaders, v_Auth, UserKey
    v_user = head['user']
    status200 = '200 OK'
    status404 = '404 Not Found'
    v_status = status200
    v_page = "hello"   
    #lookup = TemplateLookup( directories=[d], filesystem_checks=True )  # disable_unicode=True,
    #lookup = TemplateLookup( directories=[d], filesystem_checks=True, input_encoding='utf-16',output_encoding='utf-16', encoding_errors='replace'  )
    lookup = TemplateLookup( directories=[d], filesystem_checks=True, input_encoding='utf-8',output_encoding='utf-8', encoding_errors='replace'  )
  
    try:
        print('getPage - Serving : '+f+' from '+d+' .... for ...'+head['uri'])
        #template = lookup.get_template(f)
        #template = Template(lookup.get_template(f), input_encoding='utf-16', output_encoding='utf-16',encoding_errors='replace')
        #template = Template(lookup.get_template(f), lookup=lookup, input_encoding='utf-16',output_encoding='utf-16',encoding_errors='replace')
        template = lookup.get_template(f)
        
        FS = head['fieldstorage']
        FS['user'] = v_user
        #v_page = template.render(**FS).encode('utf-8', 'replace')
        v_page = template.render(**FS) #.encode('utf-16', 'replace')
        
        # !!!!!!!!!!!!!!!!!!! WORKING !!!!!!!!!!!!!!!!!!!!!!!!!!
        #mylookup = TemplateLookup(directories=['/var/NanoDev/tmp'])
        #ipage = """start Hello : <%include file="inc.txt"/> : end hello world!"""
        #mytemplate = Template(ipage, lookup=mylookup)
        #v_page = mytemplate.render(**FS).encode('utf-8', 'replace')
        
        # !!!!!!!!!!!!!!!!!!!  TEST !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        

        
        
    except exceptions.TopLevelLookupException:   #exceptions.text_error_template().render()   or   exceptions.html_error_template().render()
        print("toplevel except "+exceptions.text_error_template().render())
        v_page = v_page + "Cant find "+uri+'<br/'+exceptions.html_error_template().render()
        v_status = status404
    except:
        print("except : "+exceptions.text_error_template().render())
        v_page = v_page + exceptions.html_error_template().render()
        v_status = status404
    #v_page = cacheget('1111')
    return v_status, v_page


    
def application(environ, start_response):   
    #global head, cookieheaders, v_user, v_Auth, root
    head = parseHeader(environ)
    head = authMe(head)
    for key, value in head.iteritems():
        print 'HEADER     ', key,' : ', value
    #for key, value in environ.iteritems():
    #    print 'HEADER     ', key,' : ', value
   
    uri = head['uri']   #fulluri
    FS = head['fieldstorage']
    FSkeys = head['fieldstorageKeys']
    status200 = '200 OK'
    status404 = '404 Not Found'
    
    cookieheaders = head['cookieheaders']
    v_user = head['user']
    
#    start_response(status200, [ ('Content-type','application/json')])  # test 
#    return ['vout']                                                    # test exit
    
    # ------ Content SRC -----
    #if (uri.split('/')[0].lower() == 'shared'):
    #    d=root+'shared/'
    #    f=uri.lstrip('/shared/')  #.lstrip('/')
    #else:
    #    d=root+head['srvname']+'/'
    #    f=uri.lstrip('/')
    d=root+'/'
    f=uri.lstrip('/')
    filename=d+f
    print('filename: ',filename)
    
    # ------ RENDER -----
    if re.match(r'.*\login.xqt$', uri):
        #print('running login')
        vout = json.dumps(head['auth'])
        #print('vout === '+vout)
        start_response(status200, [ cookieheaders, ('Content-type','application/json')])
        #start_response('302 Found', [cookieheaders, ('Location','/')])
        return [vout]
    elif re.match(r'.*\logout.xqt$', uri):
        cookieheaders = genCookie(UserKey, '', head['srvname'], Expired)
        #start_response(status200, [ cookieheaders, ('Content-type','text/plain')])
        start_response('302 Found', [cookieheaders, ('Location','/')])
        return ['status = success : message = loggedout'+v_user['email']+'/'+v_user['passwd']+' : '+v_user['loggedin']]
    elif  re.match(r'.*\.XXXXhtml$', uri):  # HTML
        #re_status, re_page = getPage()
        # --- test ---
        re_status = status200
        lookup = TemplateLookup( directories=[d], filesystem_checks=True )  # disable_unicode=True,
        
        #start_response(status200, [ ('Content-type','application/json')])  # test 
        #return ['hoops']  
        try:
            print('Serving : '+f+' from '+d)
            template = lookup.get_template(f)
            filename
            FS = head['fieldstorage']
            FS['user'] = head['user'] #v_user
            #v_page = template.render(**FS).encode('utf-8')
            re_page = template.render(**FS).encode('utf-8', 'replace')
            
            #from mako.template import Template
            #mytemplate = Template(filename=filename)
            #re_page = mytemplate.render()
            
            #mytemplate = Template(file(filename).read())
            #re_page = mytemplate.render()
            
        except exceptions.TopLevelLookupException:   #exceptions.text_error_template().render()   or   exceptions.html_error_template().render()
            print("toplevel except "+exceptions.text_error_template().render())
            re_page = v_page + "Cant find "+uri+'<br/'+exceptions.html_error_template().render()
            re_status = status404
        except:
            print("except : "+exceptions.text_error_template().render())
            v_page = v_page + exceptions.html_error_template().render()
            re_status = status404
        # --- test end -----
        #start_response(re_status, [ cookieheaders, ('Content-type','text/html')])
        #start_response(status200, [ cookieheaders, ('Content-type',guess_type(uri))])
        #if os.path.isfile(filename):
        #    return [file(filename).read()]
        #else:
        #    return ['file not found : '+uri]
        start_response(re_status, [ cookieheaders, ('Content-type','text/html')])
        return [re_page]

    elif  re.match(r'.*\.html$', uri):  # HTML
        re_status, re_page = getPage(d,f, head)
        start_response(re_status, [ cookieheaders, ('Content-type','text/html')])
        return [re_page]
    else:                               # All Else
        #if ul=uri.split("/")[1]
        #u = re.sub(r'^\/+', '', uri)
        #filename = os.path.join(root+head['srvname']+head['scriptname']+'/'+head['srvname'], u)
        print 'Serving pFile : ', filename
        start_response(status200, [ cookieheaders, ('Content-type',guess_type(uri))])
        #start_response(status200, [('Content-type',guess_type(uri) )])
        if os.path.isfile(filename):
            return [file(filename).read()]
        else:
            return ['file not found : '+uri]

"""    
    status = '200 OK' 
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)
    uri = environ.get('PATH_INFO', '/')
    
    u = re.sub(r'^\/+', '', uri)
    #scriptname=environ.get('SCRIPT_NAME', '')
    #root = '/var/www/html_drupal8'
    #filename = os.path.join(root+scriptname+'/'+u)   #filename = u #os.path.join(root+head['scriptname']+'/'+head['srvname'], u)
    pwd = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(pwd+'/'+u)
    if os.path.isfile(filename):
        print 'Serving File : ', filename

        start_response('200 OK', [('Content-Type', guess_type(uri))] ) 
        #                          ('Cache-Control', 'max-age=315360000'),
        #                          ('Cache-control','private'), 
        #                          ('Expires', 'Fri, 07 Feb 2020 14:19:41 GMT'),
        #                          ('ETag','\"240000000add63-2ea-4f4086d72ad01\"')  
        return [file(filename).read()]
    else:
        return not_found(environ, start_response)
            #
            #    
"""    

#sys.path.append('/var/www/html/example.com/application')
#os.environ['PYTHON_EGG_CACHE'] = '/var/www/html/example.com/.python-egg'

"""
extensions_map = mimetypes.types_map.copy()
extensions_map.update({'': 'text/html',}) # Default
def guess_type(path):
    #return a mimetype for the given path based on file extension.
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']






class Users(object):
    def __init__(self,INdb):
        self.db = INdb

    def get_Hashuser(self, key):
        #xuser = cache.get(key)
        #if not xuser:
        sql = 'SELECT * FROM users where idx=\''+key+'\''
        v_user = self.db.select(sql,(key,))
        #cache - must put json obj in cache
        #tuser = json.loads('{}')
        if (self.db.rowcount > 0):
            print('get_Hashuser: found user in db: '+v_user[0]['email'])
            return dict(v_user[0])
        else:
            print('get_Hashuser: couldnt find user: '+key)
            return None


    def get_Emailuser(self, email,site):
        #xuser = cache.get(hashlib.md5(key).hexdigest())
        sql='SELECT * FROM users where site IN (\'*\', \''+site+'\') and email = \''+email+'\''
        v_user = self.db.select(sql)
        if (self.db.rowcount > 0):
            print('get_Emailuser: Found USER in db: '+v_user[0]['email']+'......................'+v_user[0]['idx'])
            return dict(v_user[0])
        else:
            print('get_Emailuser: couldnt find user: '+email)
            return None


        
        
        
PCKey = 'xp'
UserKey ='xu'
EmailKey = 'email'
PwdKey='pwd'
StayKey='stay'  # &stay=true
NeverExpired = (datetime.datetime.utcnow() + datetime.timedelta(days=300000)).strftime("%a, %d %b %Y %H:%M:%S GMT")
Expired = 'Sat, 16-Jul-2011 12:55:48 GMT'
hm = HM()

"""







"""
def application(environ, start_response):
    #status = '200 OK'
    #output = 'Hello World!'
    #response_headers = [('Content-type', 'text/plain'),
    #                    ('Content-Length', str(len(output)))]
    #start_response(status, response_headers)
    #return [output]
    
    head = hm.parseHeader(environ, UserKey, PCKey, EmailKey, PwdKey, StayKey )
    uri = head['uri']   #fulluri
    FS = head['fieldstorage']
    FSkeys = head['fieldstorageKeys']
    hm.printDict(head, 'HEADER :')  #hm.printDict(environ, 'Environ :')
    root = '/media/sf_shared/wsgi/'
    
    status200 = '200 OK'
    #Def_User = json.loads('{}')
    #Def_User['loggedin'] = 'n';


    #NBNBNBNBNBN:::: need to work out logic to user IDU & IDP in url if browser does not allow cookies

    #Auth/Cookie Logic: user browses to site:
    #    PC HashID = url else cookie -- if not set in either, set random one
    #    USER HashID = url else cookie  -- if set, load user(based on HashID)
    #         -- if logged in (determined from DB or....) set user as Active -- else set default profile
    #         -- if NOT logged in - expire (& Delete) Cookie for USER HashID
    #    URL logon Credentials => superceed USER HashID set anywhere else -- set/delete based on URL
    #    is Email & PWD & Stay in URL - authenticate -- if authed, set USER HashID in cookie for this session or indefinately based on stay
    #                                                -- If NOT authed, do nothing
    #Auth
    cookieheaders = ('','')
    v_user = None
    v_Auth = {}
    if head[EmailKey] and head[PwdKey]:
        cookieheaders = hm.genCookie(UserKey, '', head['srvname'], Expired)
        auth_user = users.get_Emailuser(head[EmailKey],str(head['srvname']))
        if auth_user:
            if auth_user['passwd'] == head[PwdKey]:
                if head[StayKey]:
                    cookieheaders = hm.genCookie(UserKey, auth_user['idx'], head['srvname'],  NeverExpired)
                else:
                    cookieheaders = hm.genCookie(UserKey, auth_user['idx'], head['srvname'])
                v_user = auth_user
                print 'Auth: password match! & Stay:=', str(head[StayKey])
                v_Auth['login'] = 'success'; v_Auth['mesg'] = 'youre in'
            else:
                print 'Auth: Invalid Password!'
                v_Auth['login'] = 'fail';  v_Auth['mesg'] = 'password mismatch'

        else:
            print 'Auth: URL User not found!'
            v_Auth['mesg'] = 'no user found';  v_Auth['login'] = 'fail'
    else:
        v_Auth['login'] = 'fail'; v_Auth['mesg'] = 'no email/pwd credentials provided in URL'
        # Set User Profile - if idu & idu logged in -- use user profile, else use default
        if head[UserKey]:
            tmp_user= users.get_Hashuser(head[UserKey])
            if tmp_user:
                if tmp_user['loggedin'].lower() == 'y':
                    v_user = tmp_user

        if head[PCKey] is None:
            cookieheaders = hm.genRandomCookie(head, PCKey, NeverExpired)  # if coockie not set - set pc identification -- this shouldn't conflict with the user cookie

    if v_user is None:
        v_user = users.get_Hashuser('default')  # don't need to use db.... can just declare defualt user here
    FS['user'] = v_user  #print 'V_USER', v_user



    if re.match(r'.*\login$', uri):
        #print('running login')
        vout = json.dumps(v_Auth)
        #print('vout === '+vout)
        start_response(status200, [ cookieheaders, ('Content-type','application/json')])
        return [vout]
    elif re.match(r'.*\logout$', uri):
        cookieheaders = hm.genCookie(UserKey, '', head['srvname'], Expired)
        start_response(status200, [ cookieheaders, ('Content-type','text/plain')])
        return ['status = success : message = loggedout'+v_email+'/'+v_pwd+' : '+v_stay]

    elif  re.match(r'.*\.html$', uri):
        error_style = 'html'
        lookup = TemplateLookup(directories=[root + 'mt'], filesystem_checks=True, module_directory= root +'modules')
        try:
            print('serving : '+'/'+head['srvname']+uri)
            template = lookup.get_template('/'+head['srvname']+uri)
            start_response(status200, [cookieheaders, ('Content-type','text/html')])
            return [template.render(**FS).encode('utf-8')]
        except exceptions.TopLevelLookupException:
            start_response("404 Not Found", [])
            return ["Cant find '%s'" % uri]
        except:
            if error_style == 'text':
                start_response(status200, [('Content-type','text/plain')])
                return [exceptions.text_error_template().render()]
            else:
                start_response(status200, [('Content-type','text/html')])
                return [exceptions.html_error_template().render()]
    else:
        u = re.sub(r'^\/+', '', uri)
        filename = os.path.join(root+head['scriptname']+'/'+head['srvname'], u)
        print 'Serving File : ', filename
        start_response(status200, [('Content-type',guess_type(uri))])
        return [file(filename).read()]


    """