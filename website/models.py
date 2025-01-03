from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):                         #Employee
    id = db.Column(db.Integer, primary_key=True)         #DB primary_key ID
    email = db.Column(db.String(50), unique=True)        #이름대신 ID로 사용함
    name = db.Column(db.String(50),nullable=False)       #이름
    department = db.Column(db.String(50))                #소속부서
    position = db.Column(db.String(50))                  #직책
    password = db.Column(db.String(50))                  #패스워드
    authority = db.Column(db.String(10))                 #권한관리 : 1 슈퍼 관리자, 2 관리자, 3 일반 사용자
 
