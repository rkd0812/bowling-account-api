from flask import request, jsonify, render_template
from flask_restful import Resource
from api.model.account import Account, AccountSchema

from api import db
from sqlalchemy.exc import IntegrityError
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

account_schema = AccountSchema()


class AccountApi(Resource):
    def get(self, user_id):
        account = Account.query.filter_by(user_id=user_id).first()
        return jsonify(account_schema.dump(account))

    def delete(self, user_id):
        deleted_account = Account.query.filter_by(user_id=user_id).first()
        if deleted_account is None:
            return {
                       "message": "Account not found"
                   }, 404

        try:
            db.session.delete(deleted_account)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            return {
                       "message": "IntegrityError on deleting user"
                   }, 409
        return {
            "message": "Successfully deleted user profile"
        }


class AccountsApi(Resource):
    def get(self):
        query_result = Account.query.all()
        accounts = [account_schema.dump(account) for account in query_result]
        return jsonify(accounts)


class AccountRegisterApi(Resource):
    def post(self):
        print("회원등록")
        exist_account = Account.query.filter_by(user_id=request.args['user_id']).first()
        if exist_account is not None:
            print("Account is already exists")
            return {
                "message": "This user id is already exists"
            }

        new_account = Account(
            user_id=request.args['user_id'],
            password=request.args['password'],
            user_name=request.args['user_name'],
            email=request.args['email'],
            mobile_number=request.args['mobile_number']
        )

        new_account.password = bcrypt.hashpw(new_account.password.encode("UTF-8"), bcrypt.gensalt())
        db.session.add(new_account)

        try:
            db.session.commit()
            send_email(new_account)
        except IntegrityError:
            db.session.rollback()
            return {
                "message": "Fail to register user because of IntegrityError on db"
            }

        return account_schema.dump(new_account)


# 인증메일 보내기
def send_email(account):
    # 메세지 내용
    msg = MIMEBase("multipart", "mixed")
    msg['Subject'] = '제목 테스트'
    htmlBody = render_template('renderMailAuth.html', user_id=account.user_id)

    # htmlFD = open('renderMailAuth.html', 'rb')
    HtmlPart = MIMEText(htmlBody, 'html', _charset='UTF-8')
    # htmlFD.close()

    msg.attach(HtmlPart)

    # 세션 생성
    # smtplib.SMTP(SMTP변수, 포트번호)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # TLS보안 설정
    s.starttls()
    # 로그인 인증
    # s.login('지메일계정','앱비밀번호')
    s.login('kymDev0124@gmail.com', 'qkcnlldrijkkdvqd')
    # 메일 보내기
    # s.sendmail('보내는메일주소','받는메일주소',메세지내용)
    s.sendmail('kymDev0124@gmail.com', account.email, msg.as_string().encode("UTF-8"))
    print('메일보내기 성공')
    # 세션종료
    s.quit()


class AccountAuthApi(Resource):
    def get(self):
        exist_account = Account.query.filter_by(user_id=request.args['user_id']).first()
        if exist_account is None:
            print("Account is None")
            return {
                "message": "This user id is None"
            }

        exist_account.email_auth_yn = 'Y'

        try:
            db.session.commit()
            print("auth success")
        except IntegrityError:
            db.session.rollback()
            return {
                "message": "Fail to register user because of IntegrityError on db"
            }

        return {
                   "message": "Mail Authorization complete"
               }, 200
