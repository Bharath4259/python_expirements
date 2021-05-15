from concurrent.futures import ThreadPoolExecutor
import asyncio
import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web
import os.path
import uuid
import yaml
import pandas as pd
import csv
import json
import smtplib
import ldap3
import inspect
import platform
from sqlalchemy import create_engine
import string
import random
# login encryption
from Crypto.Util.Padding import pad, unpad
import base64
from Crypto.Cipher import AES
from Crypto import Random
from tempfile import mkdtemp


# import all the methods
#  from methods import *
from methods import Methods
from inspect import getfullargspec


from tornado.options import define, options, parse_command_line

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

define("port", default=9999, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
CONFIG = yaml.safe_load(open('config.yaml', "r", encoding='utf-8'))
N_CORES = 10

auth_enabled = CONFIG['auth_enabled']
def auth_check(auth, decorator):
    return decorator if auth else lambda x: x

class BaseHandler(tornado.web.RequestHandler):
    """
    USE print(handler.current_user) user_name
    """

    def set_default_headers(self, *args, **kwargs):
        # self.set_header("Access-Control-Allow-Origin", "*")
        # self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Server", "Unknown")
        # self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def set_win_id(self, win_id):
        if auth_enabled:
            self.set_secure_cookie("win_id", tornado.escape.json_encode(win_id))
        else:
            self.set_secure_cookie("win_id", '"admin"')


    def get_win_id(self):
        if auth_enabled:
            return tornado.escape.json_decode(self.get_secure_cookie("win_id"))
        else:
            return tornado.escape.json_decode('"admin"')
    
    def get_auth_flag(self):
        return auth_enabled

    def get_current_user(self):
        if self.get_secure_cookie("user"):
            return tornado.escape.json_decode(self.get_secure_cookie("user"))
        else:
            return self.get_secure_cookie("user")

    def get_meta_var(self, var_name='app_name'):
        """
        Store non-secret variables in config meta map
        this function returns it to overall app.
        Note: do not store sensitive data like connection string or passwords
        """
        return CONFIG.get('meta', {}).get(var_name)

    def decode_data(self, data):
        res_data = {}
        for k, v in data.items():
            res_k = k.replace("[]", "")
            if len(v) > 1:
                res_data[res_k] = [x.decode('utf-8') for x in v]
            else:
                res_data[res_k] = v[0].decode('utf-8')
        return res_data


class MainHandler(BaseHandler):
    
    @auth_check(auth_enabled, tornado.web.authenticated)
    def get(self):
        if auth_enabled:
            if not self.current_user:
                self.redirect("/login/")
            else:
                self.redirect("/home/")
        else:
            self.redirect("/home/")

        # name = self.current_user
        # self.write("Hello, " + name)


class AuthLoginHandler(BaseHandler):

    BLOCK_SIZE = 16
    key = b"1234567890123456"  # TODO change to something with more entropy

    # def pad(self, data):
    #     length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    #     return bytes(data + chr(length)*length, 'utf-8')

    # def encrypt(self, message, key):
    #     IV = Random.new().read(BLOCK_SIZE)
    #     aes = AES.new(key, AES.MODE_CBC, IV)
    #     return base64.b64encode(IV + aes.encrypt(pad(message)))

    def unpad(self, data):
        return data[0:-ord(data[-1:])]

    def decrypt(self, encrypted, key):
        encrypted = base64.b64decode(encrypted)
        IV = encrypted[:self.BLOCK_SIZE]
        aes = AES.new(key, AES.MODE_CBC, IV)
        return self.unpad(aes.decrypt(encrypted[self.BLOCK_SIZE:])).decode('utf-8')

    def get(self):
        self.verify_id = self.get_argument('verify_id', None)
        if self.verify_id is not None:
            # user = enc.verify_token(verify_id)
            user = self.verify_id
            if user != None:
                self.set_current_user(user)
                self.redirect("/home/")
            else:
                error_msg = u"?error=" + \
                    tornado.escape.url_escape("Incorrect Token")
                self.redirect(u"/login/" + error_msg)
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("static/html/login.html", errormessage=errormessage)

    def ldap_auth(self, user, password, auth_conf):
        server = ldap3.Server(auth_conf['host'], get_info=ldap3.NONE)
        conn = ldap3.Connection(
            server, auth_conf['user_dn'].format(user), password)
        conn.bind()
        result = conn.search(auth_conf['search_base'],
                             auth_conf['search_filter'].format(user), attributes=ldap3.ALL_ATTRIBUTES)
        if not result or not len(conn.entries):
            return (False, None)
        return (True, user)

    def check_permission(self, password, username):
        auth_mechanism = 'basic'
        auth_conf = None

        for key, val in CONFIG['url'].items():
            if 'mechanism' in val:
                auth_mechanism = val.get('mechanism', 'basic').lower()
                auth_conf = val

        if auth_mechanism == 'basic':
            if username == "admin" and password == "admin":
                self.set_win_id("Admin")
                return True
            else:
                return False
        elif auth_mechanism.lower() == 'ldap':
            resp = self.ldap_auth(username, password, auth_conf.get('kwargs'))
            if resp[0]:
                self.set_win_id(username)
                return True
            return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        password = self.decrypt(password, self.key)
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            # compass_validator.setting_email()
            self.redirect("/home/")
        else:
            error_msg = u"?error=" + \
                tornado.escape.url_escape("Login incorrect")
            self.redirect(u"/login/" + error_msg)

    def set_current_user(self, user):
        """
            5 mins=0.00347222
            30 mins=0.0208333
            1 hours=0.0416667
        """
        if user:
            self.set_secure_cookie(
                "user", tornado.escape.json_encode(user), expires_days=0.0208333)
        else:
            self.clear_cookie("user")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/login/"))


class FileHandler(BaseHandler):
    """
    config example ---
    app_home:
        pattern: /home/
        handler: FileHandler
        path: static/html/index.html
    _________________________________

    Serves file using the file_path form file_name variable
    """

    def initialize(self, file_name):
        self.file_name = file_name

    @auth_check(auth_enabled, tornado.web.authenticated)
    def get(self):
        self.render(self.file_name, handler=self)


class ErrorHandler(BaseHandler):

    def write_error(self, status_code, **kwargs):
        err_cls, err, traceback = kwargs['exc_info']
        self.set_status(err.status_code)
        self.render(os.path.join(
            "static", "error_html",  f"{err.status_code}.html"))

        # if err.log_message and err.log_message.startswith(custom_msg):
        #     self.write(f"<html><body><h1>{err.status_code}</h1></body></html>")


class DownloadHandler(BaseHandler):
    """
    config example ---
    app_home:
        pattern: /?filename
        handler: DownloadHandler
        path: static/html/index.html
    _________________________________

    Serves file using the file_path form file_name variable
    """

    # def initialize(self, file_name):
    #     self.file_name = file_name

    def initialize(self, function_name):
        self.function_name = function_name

    @auth_check(auth_enabled, tornado.web.authenticated)
    def get(self):
        # file_name = 'canvas.zip'
        file_name = self.func_result()
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition',
                        'attachment; filename=' + file_name)
        with open(file_name, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

    def func_result(self):

        tmp_func = getattr(globals()['Methods'](), self.function_name)

        tmp_args = {}
        for arg in getfullargspec(tmp_func)[0]:
            if arg == 'FormHandler':
                tmp_args[arg] = FormHandler
            elif arg == 'BaseHandler':
                tmp_args[arg] = BaseHandler
            elif arg == 'DownloadHandler':
                tmp_args[arg] = DownloadHandler
            elif arg != 'self':
                tmp_args[arg] = self.get_argument(arg)

        # If varargs
        if getfullargspec(tmp_func)[1]:
            return tmp_func(**tmp_args, **self.request.arguments)
        else:
            return tmp_func(**tmp_args)


class FunctionHandler(BaseHandler):
    """
    config example ---
    get_friction_df:
        pattern: /get_friction_df
        handler: FunctionHandler
        function: get_friction_df
    _________________________________

    call respective function once the fn call is made
    use globals()['fn_name'](args)

    DIRECT CALL
    tmp_func = globals()['function_name']
    tmp_func.__code__.co_varnames

    FROM CLASS
    tmp_func = globals()['function_name']
    tmp_func.__code__.co_varnames

    * get arguments for the function ->  fn_name.__code__.co_varnames
    * map args
    * call function
    """
    # function_name = 'test_handler'

    def initialize(self, function_name):
        self.function_name = function_name
        self.executor = ThreadPoolExecutor(max_workers=N_CORES)

    @auth_check(auth_enabled, tornado.web.authenticated)
    @tornado.gen.coroutine
    def get(self):
        data = yield self.executor.submit(self.func_result)
        self.write(data)
        self.finish()

    @auth_check(auth_enabled, tornado.web.authenticated)
    @tornado.gen.coroutine
    def post(self):
        data = yield self.executor.submit(self.func_result)
        self.write(data)
        self.finish()

    def func_result(self):

        tmp_func = getattr(globals()['Methods'](), self.function_name)

        tmp_args = {}
        for arg in getfullargspec(tmp_func)[0]:
            if arg == 'FormHandler':
                tmp_args[arg] = FormHandler
            elif arg == 'BaseHandler':
                tmp_args[arg] = BaseHandler
            elif arg != 'self':
                tmp_args[arg] = self.get_argument(arg)

        # If varargs
        if getfullargspec(tmp_func)[1] or self.request.arguments:
            return tmp_func(**tmp_args, **self.request.arguments)
        else:
            return tmp_func(**tmp_args)


class FormHandler(BaseHandler):
    """
    config example ---
    variables:
        connection_string: "mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BODBC%20...

    # POST METHOD
    update_report_feature:
        pattern: /report_features # Maps /db/table to {_0:db, _1:table}
        handler: FormHandler
        kwargs:
        table: report_features
        id: [win_id, report_id]
    _________________________________
    store all the queries inside "queries.yaml"



    Handler for getting data for the specified section
    section refers to key stored in query.yaml
    url-params are processed and sotered as args
    data is obtained after running the query with the args
    """

    def initialize(self, table_name="", cols=[]):
        self.table_name = table_name
        self.columns = cols

    @auth_check(auth_enabled, tornado.web.authenticated)
    async def get(self):
        """Get Data for selected section."""
        section = self.get_argument('section', 'NA')
        try:
            url, sql, params = self.process_filters(section)
        except:
            _config = yaml.safe_load(
                open('queries.yaml', "r", encoding='utf-8'))
            params = self.decode_data(self.request.arguments)
            merged_params = _config[section].get('default', {}).copy()
            merged_params.update(params)
            url = CONFIG.get('variables')['connection_string']
            sql = _config.get(section)['query'].format(**merged_params)
            print(f'QUERY: {sql}')

        data = await self.filter(url, sql, params)
        self.write(data.to_json(orient='records'))
        self.finish()

    @auth_check(auth_enabled, tornado.web.authenticated)
    async def put(self):
        """update data

        query = "UPDATE table_name SET column1 = value1, column2 = value2, ...
        WHERE condition;"
        """
        url = CONFIG.get('variables')['connection_string']
        engine = create_engine(url)

        # _keys = []
        # _values = []
        _set = []
        _where = []
        for k, v in self.request.arguments.items():
            # _keys.append(k)
            # _values.append("{}".format(v[0].decode()))
            _ = v[0].decode()
            _val = "'{}'".format(_) if type(_) != int else _
            if k in self.columns:
                _where.append("{col}={val}".format(col=k, val=_val))
            else:
                _set.append("{col}={val}".format(col=k, val=_val))

        put_query = """UPDATE {table}
         SET {_set} WHERE {_where}
         """.format(table=self.table_name,
                    _set=",".join(_set),
                    _where=" AND ".join(_where))
        print(f'QUERY: {put_query}')
        engine.execute(put_query)

    @auth_check(auth_enabled, tornado.web.authenticated)
    async def post(self):
        """INSERT data
        query = "INSERT INTO table_name (column1, column2, column3, ...)
        VALUES (value1, value2, value3, ...);"
        """
        url = CONFIG.get('variables')['connection_string']
        engine = create_engine(url)

        _keys = []
        _values = []
        for k, v in self.request.arguments.items():
            _ = v[0].decode()
            _val = "'{}'".format(_) if type(_) != int else _
            _keys.append(k)
            _values.append(_val)

        put_query = """INSERT INTO {table}
         ({_col}) VALUES ({_val});""".format(table=self.table_name,
                                             _col=",".join(_keys),
                                             _val=",".join(_values))
        print(f'QUERY: {put_query}')
        engine.execute(put_query)

    @auth_check(auth_enabled, tornado.web.authenticated)
    async def delete(self):
        """delete row
        query = "DELETE FROM table_name WHERE condition;"
        """
        url = CONFIG.get('variables')['connection_string']
        engine = create_engine(url)

        _where = []
        for k, v in self.request.arguments.items():
            # _keys.append(k)
            # _values.append("{}".format(v[0].decode()))
            _ = v[0].decode()
            _val = "'{}'".format(_) if type(_) != int else _
            _where.append("{col}={val}".format(col=k, val=_val))

        del_query = """DELETE FROM {table}
         WHERE {_where}""".format(table=self.table_name,
                                  _where=" AND ".join(_where))
        print(f'QUERY: {del_query}')
        engine.execute(del_query)

    def connect_engine(self):
        """
        create sql engine
        let this throw an error if connection string is not present
        """
        return create_engine(CONFIG.get('variables')['connection_string'])

    async def filter(self, url, sql, params={}):
        """Filter data from table."""
        engine = create_engine(url)
        return pd.read_sql(sql, engine)

    def process_filters(self, section):
        """Format the filter params."""
        process = {
            'first': lambda vals: [vals[0]],
            'join_with_comma': lambda vals: [",".join("'{}'".format(val)
                                                      for val in vals)],
            'sep_with_comma': lambda vals: [",".join('{}'.format(val)
                                                     for val in vals)]
        }
        _config = yaml.safe_load(open('queries.yaml', "r", encoding='utf-8'))
        filters = self.get_params(_config.get(section))['filters']

        default_filters = _config[section].get('default', {}).copy()
        default_filters.update(filters)
        result = {key: process[_config[section].get('process', {}).get(key, 'first')](vals)
                  if key in _config[section].get('process', []) and
                  vals != _config[section]['default'][key] else vals
                  for key, vals in default_filters.items()}
        _params = {k: v[0] for k, v in result.items() if len(v) > 0}
        url = CONFIG.get('variables')['connection_string']
        sql = _config.get(section)['query'].format(**_params)
        print(f'QUERY: {sql}')
        return url, sql, _params

    def get_params(self, _config):
        """
        get params from url.
        over-ride params when present in url
        """

        # ENH: eliminate need for using extra keys for defaults
        # filter_dict = {k: self.get_argument(k, v) for k, v in _config['filters'].items()}
        # {k: self.get_argument(k, v) for k, v in filter_dict.items()}
        filter_dict = {k: self.get_argument(k, v)
                       for k, v in _config.get('default', {}).items()}
        for k, v in filter_dict.items():
            # if v == list:
            #     filter_dict[k] = v.split(",")
            if type(v) == str:
                filter_dict[k] = [v]
            else:
                filter_dict[k] = v

        # filter_dict = {k: v.split(",") for k, v in filter_dict.items() if  (v ==str and  v.lower() != 'all') and v != ''}

        print(filter_dict)
        default_filters = _config.copy()
        default_filters['filters'] = filter_dict
        return default_filters


class UploadHandler(BaseHandler):
    """
    config example ---
    upload_excel:
        pattern: /upload
        handler: UploadHandler
        path: static/uploads
    _________________________________

    upload file to selected path -- work with post request and html form
    """

    def initialize(self, storage_path):
        self.storage_path = mkdtemp(dir=CONFIG['storage_path'])

    async def post(self):
 
        uploaded_files = []

        listOfFiles = [fl for fl in self.request.files.keys()]
        for f in listOfFiles:
            file1 = self.request.files[f]
            original_fname = file1[0]['filename']
            extension = os.path.splitext(original_fname)[1]
            f_name = os.path.splitext(original_fname)[0]
            display_filename = f'{f_name}{extension}'
            f_path = os.path.join(
                self.file_path, final_filename)
            print(f_path)
            async with aiofiles.open(f_path, "wb") as f:
                await f.write(file1[0]["body"])
            uploaded_files.append(display_filename)

        self.finish(json.dumps({'resp': "success", 
                                'data_files': uploaded_files
                            }))


class DownloadHandler(BaseHandler):
    """
    config example ---
    app_home:
        pattern: /?filename
        handler: DownloadHandler
        path: static/html/index.html <<direct file path>>
        function: function_name      <<name of function to create file & return file path>>
    _________________________________

    Serves file using the file_path form file_name variable
    """

    def initialize(self, **kwargs):
        # self.function_name = function_name
        self.function_name = kwargs.get('function_name')
        self.path = kwargs.get('path')
        self.headers = kwargs.get('headers', {})


    @tornado.web.authenticated
    def get(self):
        # file_name = 'canvas.zip'
        if(self.path):
            file_name = self.path
        else:
            file_name = self.func_result()
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition',
                        'attachment; filename=' + file_name)
        if not file_name or not os.path.exists(file_name):
            raise HTTPError(404)
        with open(file_name, 'rb') as f:
            try:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)
            except:
                raise HTTPError(404)
        self.finish()

    def func_result(self):
        tmp_func = getattr(globals()['Methods'](), self.function_name)
        tmp_args = {}
        for arg in getfullargspec(tmp_func)[0]:
            if arg == 'FormHandler':
                tmp_args[arg] = FormHandler
            elif arg == 'BaseHandler':
                tmp_args[arg] = BaseHandler
            elif arg == 'DownloadHandler':
                tmp_args[arg] = DownloadHandler
            elif arg != 'self':
                tmp_args[arg] = self.get_argument(arg)

        # If varargs
        if getfullargspec(tmp_func)[1]:
            return tmp_func(**tmp_args, **self.request.arguments)
        else:
            return tmp_func(**tmp_args)


def make_app():
    """ return app url with the class
    [
        (r"/", FileHandler),
        (r"/mak", MakHanlder),
        (r"/a/message/new", MessageNewHandler),
        (r"/a/message/updates", MessageUpdatesHandler),
    ],
    """

    h_c = CONFIG['url']
    app_list = [(r"/", MainHandler)]
    for key in h_c.keys():
        handler = h_c[key]

        h = globals()["{}".format(handler['handler'])]
        if handler.get('handler') == 'FunctionHandler':
            app_list.append((r"{}".format(handler['pattern']),
                             h,  dict(function_name=handler['function'])))
        elif handler.get('handler') == 'DownloadHandler':
            app_list.append((r"{}".format(handler['pattern']),
                             h,  dict(function_name=handler['function'])))
        elif handler.get('handler') == 'FileHandler':
            app_list.append((r"{}".format(handler['pattern']),
                             h,  dict(file_name=handler['path'])))
        elif handler.get('handler') == 'UploadHandler':
            app_list.append((r"{}".format(handler['pattern']),
                             h,  dict(storage_path=handler.get('path', 'static/uploads'))))
        elif handler.get('handler') == 'DownloadHandler':
            app_list.append((r"{}".format(handler['pattern']),
                             h,  dict(
                                    path=handler.get('path', None),
                                    function_name=handler.get('function', None),
                                    headers=handler.get('headers', {})
                                 )))
        elif handler.get('handler') == "FormHandler":
            app_list.append((r"{}".format(handler['pattern']), h,
                             dict(
                table_name=handler.get('kwargs', {}).get('table'),
                cols=handler.get('kwargs', {}).get('id')
            )))
        else:
            app_list.append((r"{}".format(handler['pattern']),  h))
    return app_list


def main():
    # os.system("start /B start cmd.exe @cmd /k node static/js/chromecapture.js")
    parse_command_line()

    # random_cookie_secret
    characters = string.ascii_letters + string.punctuation + string.digits
    cook_sec = ""
    cook_sec_length = random.randint(20, 30)

    for _ in range(cook_sec_length):
        char = random.choice(characters)
        cook_sec = cook_sec + char

    app = tornado.web.Application(
        make_app(),
        # cookie_secret=cook_sec,
        cookie_secret="cook_sec",
        login_url="/login/",
        template_path=os.path.join(os.path.dirname(__file__), ""),
        static_path=os.path.join(os.path.dirname(__file__), "static/"),
        # xsrf_cookies=True,
        debug=options.debug,
        default_handler_class=ErrorHandler,
        serve_traceback=False
    )
    if not auth_enabled:
        print(f"Authentication is turned off for the App")
    print(f"Application has been launched on port {options.port}")
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
