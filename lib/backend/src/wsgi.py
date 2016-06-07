from server import app as application
from config import HOST, \
                   PORT, \
                   DEBUG

if __name__ == '__main__':
    application.run(host=HOST,
            port=PORT,
            debug=DEBUG)

