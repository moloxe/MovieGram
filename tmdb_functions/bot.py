import logging
from tmdb import getMovie, getSerie, getPeople, getTrendMovies, getTrendSeries
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


class MovieGramBot():
    def __init__(self):
        # no nos hackeen porfi t.t
        self.token_ = '857019165:AAHkHPXfVU-iw6yb7EP5GOtQzXz4LJ8h03k'
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.reply_keyboard = [['Serie', 'Pelicula'],
                               ['Celebridad', 'Top Peliculas'],
                               ['Top Series', 'Adios']]

        self.markup = ReplyKeyboardMarkup(
            self.reply_keyboard, one_time_keyboard=True)

    def start(self, update, context):
        update.message.reply_text(
            "Hola! Soy MovieGram bot. Estoy aqui para ayudarte en tus aventuras cinefilas",
            reply_markup=self.markup)

        return CHOOSING

    def regular_choice(self, update, context):
        text = update.message.text
        context.user_data['choice'] = text
        if(text != 'Pelicula' and text != 'Serie' and text != 'Celebridad'):

            if(text == 'Top Peliculas'):
                data = getTrendMovies()
            elif(text == 'Top Series'):
                data = getTrendSeries()

            ##############

            for item in data:
                msj += item['title'] + ": " + item["overview"]
                ph = item['image']
                update.message.reply_text(msj, reply_markup=self.markup)
                update.message.reply_text(ph)
                msj = ""

            return CHOOSING

        update.message.reply_text(
            'Por favor dime el nombre de la {} que estas buscando!'.format(text.lower()))
        return TYPING_REPLY

    def received_information(self, update, context):
        user_data = context.user_data
        text = update.message.text
        category = user_data['choice']
        del user_data['choice']
        ph = 'https://indiehoy.com/wp-content/uploads/2018/09/nicolas-cage-meme-640x434.jpg'
        msj = 'Genial! Entonces buscas la ' + category + \
            ' llamada ' + text + '...Encontré esto: \n'
        text = text.replace(' ', '+')
        if(category == 'Pelicula'):
            js = getMovie(text)
            if(js != None):
                msj += js['title'] + ": " + js["overview"]
                ph = js['image']
        elif(category == 'Serie'):
            js = getSerie(text)
            if(js != None):
                msj += js['title'] + ": " + js["overview"]
                ph = js['image']
        elif(category == 'Celebridad'):
            js = getPeople(text)
            if(js != None):
                msj += js['name'] + ", Popularidad: " + str(js["popularity"])
                ph = js['image']
            return CHOOSING

        if(js == None):
            msj = 'No se encontro nada'

        update.message.reply_text(msj, reply_markup=self.markup)
        update.message.reply_text(ph)
        return CHOOSING

    def done(self, update, context):
        update.message.reply_text("Espero haberte ayudado, hasta luego")
        return ConversationHandler.END

    def error(self, update, context):
        self.logger.warning('Update "%s" caused error "%s"',
                            update, context.error)

    def run(self):
        updater = Updater(self.token_, use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],

            states={
                CHOOSING: [MessageHandler(Filters.regex('^(Serie|Pelicula|Celebridad|Top Peliculas|Top Series)$'),
                                          self.regular_choice)],

                TYPING_CHOICE: [MessageHandler(Filters.text,
                                               self.regular_choice)
                                ],

                TYPING_REPLY: [MessageHandler(Filters.text,
                                              self.received_information),
                               ],
            },

            fallbacks=[MessageHandler(Filters.regex('^Adios$'), self.done)]
        )

        dp.add_handler(conv_handler)
        dp.add_error_handler(self.error)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    obj = MovieGramBot()
    obj.run()
