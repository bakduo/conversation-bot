from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'root': {
        'level': 'DEBUG'
    }
})

from service.telegram_srv import BotCustom

process_bot = BotCustom.get_instance()
process_bot.initCommand()
process_bot.run()
