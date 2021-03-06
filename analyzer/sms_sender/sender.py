from django.core.mail import send_mail
from django.template.loader import render_to_string
from zeep import Client

from collection.models import Collections
from core import mixins
from core.utils import validate_sms_phone
from settings_analyzer.models import Settings


class SmsSender:
    # text = 'Готовы выкупить ваше авто, 90% рыночной стоимости, ' \
    #        'деньги в день обращения. 0672323060, 0932714661'
    text = Settings.get_solo().message_text

    def __init__(self):
        self.error_message = ''
        self.never_send = False
        self.msg_status = ''
        self.msg_id = ''
        self.client = Client('http://turbosms.in.ua/api/wsdl.html')
        self.auth = self.client.service.Auth(login='analyzer',
                                             password='eX10i#FO#@4J')
        self.balance = self.get_balance()

    def send(self, phone):
        enable_disable_sms = Settings.get_solo().enable_disable_sms
        if enable_disable_sms:
            if self.auth == 'Вы успешно авторизировались':
                if float(self.balance):
                    return self._result(phone)
                else:
                    self.error_message = f'Ваш баланс {self.balance}'
            elif self.auth == 'Неверный логин или пароль':
                self.error_message = 'Неверный логин или пароль'
        else:
            self.never_send = True

    def _result(self, phone):
        result = self.client.service.SendSMS(sender='Top Vykup',
                                             destination=phone,
                                             text=self.text)
        if result[0] == 'Сообщения успешно отправлены':
            self.msg_status = self.get_msg_status(result[1])
            self.msg_id = result[1]
            return True
        else:
            self.error_message = result[0]

    def get_msg_status(self, sms_id):
        self.msg_status = self.client.service.GetMessageStatus(
            MessageId=sms_id)
        return self.msg_status

    def get_balance(self):
        return self.client.service.GetCreditBalance()


class ClientSmsSender(mixins.EmailSenderMixin):
    def __init__(self):
        super().__init__()
        self.collections = Collections.objects.filter(
            sms_is_send=False, never_send=False).order_by('create_at')
        self.email_enable = Settings.get_solo().enable_disable_email

    def start(self):
        sms = SmsSender()

        self.check_email()

        for collection in self.collections:

            phone = validate_sms_phone(collection)

            if phone:
                sms_status = sms.send(phone)
                if sms_status:
                    error = collection.phones.get('error')
                    if error:
                        collection.phones['error'] = ''
                    collection.sms_is_send = True

                    if self.email_enable:
                        if not collection.email_is_send:
                            self.send_email_to_admin(collection)

                else:
                    collection.phones['error'] = sms.error_message
            collection.save()

    def check_email(self):
        collections = Collections.objects.filter(sms_is_send=True,
                                                 never_send=False,
                                                 email_is_send=False
                                                 )
        for collection in collections:
            self.send_email_to_admin(collection)
