# coding:utf-8
# TODO:
# 1. create a filter condition - when the subscription window may work
# 2. display a subscription window
# 3. create a handler for the new subribtion:
# in: email, do: send verification email
# 4. create a handler for verification link
# 5. create the sender
from helpers import send_email
from random import randint


class Subscriptor(object):
    def check_filter(self, f):
        return False
        # if f.price_max > f.price_min + 100000:
        #     return False
        # if len(f.stations) == 0 or len(f.stations) > 50:
        #     return False
        # return True

    def _generate_activation_message(self, filter_params, secret_link):
        return ''.join([
            u"Здравствуйте!<br><br>",
            u"Кто-то, возможно вы, подписался на обновления на сайте <a href='http://homeseek.ru'>HomeSeek.</a>",
            u"Если это были не вы, то проигнорируйте это письмо.<br>",
            u"Иначе, пройдите, пожалуйста, по ссылке: ",
            u"<a href='{}'>активация подписки.</a><br><br>".format(secret_link),
            u"С уважением, ваш HomeSeek.",
        ])

    def create_new(self, db, filter_params, email):
        code = randint(1000000, 9999999)
        inserted = db.subscriptions.insert_one({
            'email': email,
            'verified': False,
            'filter_params': filter_params,
            'code': code
        })
        secret_link = 'http://homeseek.ru/a?t={}&c={}'.format(inserted.inserted_id, code)
        send_email(
            src=u'robot.homeseek@yandex.ru',
            dst=email,
            subj=u'Подтверждение подписки на homeseek.ru',
            message=self._generate_subscription_message(filter_params, secret_link),
        )
        return True
