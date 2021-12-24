import sys
from app import app


def create_app():
    return app


if __name__ == '__main__':
    app.run(port=sys.argv[1], debug=True)
