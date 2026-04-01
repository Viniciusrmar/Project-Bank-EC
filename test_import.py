import os, sys
print('cwd', os.getcwd())
print('files', os.listdir('.'))
try:
    import config
    print('config module', config)
    print('config file', config.__file__)
except Exception as e:
    print(type(e).__name__, e)
