import telegram
from config.config import CONFIG_APP
import logging
import requests
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.updater import Updater
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.bot import Bot
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import re
from .control_srv import GeoAPI
from .control_srv import ControlCode
from .control_srv import ControlStock

WELCOME = 0
SOLICITAR_PRODUCTO = 1
MENCIONA_CODIGO = 2
CANCEL = 3
CORRECT = 4

yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)
caracteres_regex = re.compile(r'^[a-z]$')

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class BotCustom(metaclass=SingletonMeta):

    def __init__(self):
        super()
        self.token = CONFIG_APP["app"]["token"]
        self.user = CONFIG_APP["app"]["user"]
        self.url = CONFIG_APP["app"]["url"]
        self.port = CONFIG_APP["app"]["port"]
        logging.debug(self.user)
        logging.debug(self.url)
        self.updater = Updater(self.token,
                  use_context=True)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def solicitar_producto(self,update_obj, context):
        try:
            logging.debug("Estas en solicitar producto")
            logging.debug(update_obj.message.text)
            first_name = update_obj.message.from_user['first_name']
            
            if update_obj.message.text.lower() in ['no', 'n']:
                logging.debug("Estas cancelando la operacion")
                update_obj.message.reply_text("Usted {}, decidio no seguir.".format(first_name))
                return CANCEL

            control = ControlStock()
            items = update_obj.message.text.split(",")
            if (len(items)==2):
                try:    
                    if not isinstance(int(items[1]), int):
                        update_obj.message.reply_text("usted: {}, ha solicitado un producto {}, aunque la cantidad no ha sido ingresada, este debe ser un numero entero. Vuelva a intentarlo. Para no continuar ingrese (n,No)".format(first_name,update_obj.message.text))
                        return SOLICITAR_PRODUCTO
                except Exception as e:
                    logging.debug("El parametro no es correcto")
                    update_obj.message.reply_text("usted: {}, ha solicitado un producto {}, aunque la cantidad no ha sido ingresada, este debe ser un numero entero. Vuelva a intentarlo. Para no continuar ingrese (n,No).".format(first_name,update_obj.message.text))
                    return SOLICITAR_PRODUCTO

                if control.is_product_available(items[0],int(items[1])):
                    update_obj.message.reply_text("usted: {}, ha solicitado el producto {}, esta disponible, ahora ingrese un codigo de descuento: ".format(first_name,update_obj.message.text))
                    return MENCIONA_CODIGO
                else:
                    update_obj.message.reply_text("usted: {}, ha solicitado un producto {}, que no esta disponible para consumir. Vuelva a intentarlo:".format(first_name,update_obj.message.text))
                    return SOLICITAR_PRODUCTO
            else:
                update_obj.message.reply_text("usted debe ingresar un producto y una cantidad ejemplo 'frutilla,10', vuelva a intentarlo. Para no continuar ingrese (n,No).")
                return SOLICITAR_PRODUCTO

        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al solicitar producto")
    
    def menciona_codigo(self,update_obj, context):
        try:
            logging.debug("Estas en validar codigo")
            logging.debug(update_obj.message.text)
            controlCode = ControlCode()
            if (controlCode.validate_discount_code(update_obj.message.text)):
                update_obj.message.reply_text("menciona producto : {}. Desea confirmarlo?(Yes / No)".format(update_obj.message.text))
                return CORRECT
            else:
                update_obj.message.reply_text("El codigo {} no es valido, vuelva a ingresarlo...".format(update_obj.message.text))
                return MENCIONA_CODIGO
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al mencionar codigo")

    def correct(self,update_obj, context):
        try:    
            logging.debug("Estas en correct")
            if update_obj.message.text.lower() in ['yes', 'y']:
                update_obj.message.reply_text("producto Confirmado!!!")
            else:
                update_obj.message.reply_text("Producto descartado")

            first_name = update_obj.message.from_user['first_name']
            update_obj.message.reply_text(f"Hasta la proxima {first_name}, que tengas un buen dia.")
            return ConversationHandler.END
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al usar correct")

    def cancel(self,update_obj, context):
        try:    
            logging.debug("Estas en cancel")
            first_name = update_obj.message.from_user['first_name']
            update_obj.message.reply_text("Usted {} a cancelado la operacion!".format(first_name))
            return ConversationHandler.END
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al usar cancel")

    def initCommand(self):
        try:
            dispatcher: Dispatcher = self.updater.dispatcher
            custom_hander = ConversationHandler(
                    entry_points=[CommandHandler('start', self.start)],
                    states={
                    WELCOME: [MessageHandler(Filters.text, self.welcome)],
                    SOLICITAR_PRODUCTO: [MessageHandler(Filters.text, self.solicitar_producto)],
                    MENCIONA_CODIGO: [MessageHandler(Filters.text, self.menciona_codigo)],
                    CANCEL: [MessageHandler(Filters.text, self.cancel)],
                    CORRECT: [MessageHandler(Filters.regex(yes_no_regex), self.correct)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            )
            dispatcher.add_handler(custom_hander)
            dispatcher.add_error_handler(self.error)
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al usar initCommand")


    def error(bot, update, error):
        logging.debug("Error handle: {} causa: {}".format(update, error))
        

    def start(self,update: Update, context: CallbackContext):
        try:    
            logging.debug("Comando start")
            bot: Bot = context.bot
            bot.send_message(
                chat_id=update.effective_chat.id,
                text="Hola este es un Bot de la Heladerías Frozen SRL, para continuar ingrese (yes,no)."
            )
            return WELCOME
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al usar start")

        
    def welcome(self,update_obj, context):
        try:    
            logging.debug("Estas en bienvenido1")
            logging.debug(update_obj.message.text)
            if update_obj.message.text.lower() in ['yes', 'y']:    
                if (GeoAPI.is_hot_in_pehuajo()):
                    logging.debug("Enviando mensaje de bienvenida Hot > 28 grados celcius")
                    update_obj.message.reply_text("Bienvenido a un lindo dia de sol con temperatura de > a 28 grados celcius, por favor ingrese un producto:")
                else:
                    logging.debug("Enviando mensaje de bienvenida < a 28 grados celcius")
                    update_obj.message.reply_text("Bienvenido su temp actual es < a 28 grados celcius, por favor ingrese un producto:")
                return SOLICITAR_PRODUCTO
            else:
                return CANCEL
        except Exception as e:
            logging.debug(e)
            raise Exception("Exception al dar la bienvenida")
        
    def get_token(self):
        return self.token

    def get_url(self):
        return self.url

    def get_user(self):
        return self.user

    def get_bot(self):
        return self.bot;
    
    def process_one(self,data):
        print(data)
        return str(data).upper()

    @staticmethod
    def get_instance():
        return BotCustom()
