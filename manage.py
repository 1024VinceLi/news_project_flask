from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


class Config(object):
    """配置信息类"""
    DEBUG = True

    # 配置mysql信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news_infor"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# 从类中导入配置信息
app.config.from_object(Config)

# 获取db
db = SQLAlchemy(app)


@app.route('/')
def index():
    return "index"


if __name__ == '__main__':
    app.run(debug=True)