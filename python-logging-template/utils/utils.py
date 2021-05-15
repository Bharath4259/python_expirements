import logger

app_name = 'MyAwesomeApp'
app_log = logger.Logger(app_name)
my_custom_app_log = app_log.create_applevel_logger(file_name='app_debug.log')


