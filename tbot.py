import os
import pickle
import time

import rdflib.graph as g
import requests
import telepot
from geopy.distance import great_circle
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


def read_monuments():
    with open("./data/monuments3.pickle", "rb") as file:
        return pickle.load(file)


def info_monument(monument_id, search):
    result = g.Graph()
    result.parse("../data/dataset.ttl", format="ttl")
    query_text = (
        """
        ask where {
            ?m a cis:CulturalInstituteOrSite ;
            dc:identifier
        """
        + monument_id
        + """ ;
                     """
        + search
        + """ ?x .
                }
            """
    )
    query = result.query(query_text)
    for r in query:
        if r:
            query_text = (
                """
                        select distinct ?x where {
                            ?m a cis:CulturalInstituteOrSite ;
                            dc:identifier """
                + monument_id
                + """ ;
                            """
                + search
                + """ ?x .
                        }
                    """
            )
            query = result.query(query_text)
            result_query = {}
            result_query[monument_id] = list()
            for row in query:
                if row[0] == "":
                    return -1
                a = row[0]
                result_query[monument_id].append(a)
            return result_query
        else:
            return -1


def id_monument(monument_name):
    result = g.Graph()
    result.parse("./data/dataset.ttl", format="ttl")
    result_query = {}
    result_query[monument_name] = list()
    query_text = (
        """
                    select distinct ?id where {
                    """
        + monument_name
        + """ a cis:CulturalInstituteOrSite ;
                    dc:identifier ?id
                }
            """
    )
    query = result.query(query_text)
    for row in query:
        result_query[monument_name].append(row[0])
    return result_query


def check_more_img(query_data):
    if info_monument(query_data, "pmo:nearbyCulturalInstituteOrSite") != -1:
        more_picture = info_monument(query_data, "pmo:nearbyCulturalInstituteOrSite")
        for x in range(0, len(more_picture[query_data]), 1):
            string = "<" + str(more_picture[query_data][x]) + ">"
            monument = id_monument(string)
            monument_id = monument[string][0]
            if info_monument(monument_id, "pmo:picture") != -1:
                return 1
    return -1


def send_monument_nearby(bot, updates):
    last_positions[updates["chat"]["id"]] = (
        updates["location"]["latitude"],
        updates["location"]["longitude"],
    )
    nearby_list = list()
    chat = updates["chat"]["id"]
    # print("CHAT ID: {}".format(chat))
    mypos = (updates["location"]["latitude"], updates["location"]["longitude"])
    # print(mypos)
    for placemark in monuments:
        placepos = (placemark["latitudine"], placemark["longitudine"])
        dist = great_circle(mypos, placepos).meters
        if dist < 300:
            nearby_list.append(placemark)
            # bot.sendMessage(chat, placemark["nome"])
            # bot.sendLocation(chat, placemark["latitudine"], placemark["longitudine"])
    if not nearby_list:
        bot.sendMessage(
            chat,
            "Mi dispiace, nel raggio di 300 metri non sono presenti monumenti da visitare...",
        )
    else:
        send_custom_keyboard(bot, updates, nearby_list)


def send_custom_keyboard(bot, updates, monument_list):
    chat = updates["chat"]["id"]
    # keyboard = ReplyKeyboardMarkup(
    #    keyboard=[[KeyboardButton(text="{}".format(text))] for text in style]
    # )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="{}".format(text["nome"]),
                    callback_data="{}".format(text["id"]),
                )
            ]
            for text in monument_list
        ]
    )
    bot.sendMessage(chat_id=chat, text="Sei vicino a: ", reply_markup=keyboard)


"""
Callback_query viene chiamata in due casi:
Primo caso da send_custom_keyboard una volta che l'utente seleziona il monumento
d'interesse

Secondo caso in cui l'utente seleziona uno dei tre pulsanti messi a disposizione
"torna indietro" "foto storiche" e "Più immagini",
in questo caso all'interno del paccheto msg sarà presente oltre il campo id del
monumento, anche un numero identificativo, che permette di capire cosa bisogna
visualizzare, nello specifio 1 se si tratta di torna indietro, 2 foto storiche e
3 più immagini. Ad esempio se l'utente preme torna indietro il pacchetto msg avrà un
formato del tipo id/1
(supponendo che id sia formato interamente da cifre, il carattere separatore sarà / ).
"""


def on_callback_query(msg):
    # print("Dentro on_callback_query")
    query_id, from_id, query_data = telepot.glance(msg, flavor="callback_query")
    # print("Callback query: ", query_id, from_id, query_data)
    if query_data.find("/") == -1:
        # print("Non è stato premuto alcun tasto \n")
        # CONTROLLO PRESENZA PROPRIETA'
        if info_monument(query_data, "cis:institutionalName") != -1:
            monument_name = info_monument(query_data, "cis:institutionalName")
            bot.sendMessage(
                from_id, "*" + monument_name[query_data][0] + "*", parse_mode="Markdown"
            )

        if info_monument(query_data, "pmo:picture") != -1:
            monument_photo = info_monument(query_data, "pmo:picture")
            photo_link = monument_photo[query_data][0]
            if requests.get(photo_link).status_code < 400:
                bot.sendPhoto(from_id, photo_link)
        """
        else:
            bot.sendPhoto(from_id, photo=open("img/og-stemma-palermo.gif", "rb"))
        """
        if info_monument(query_data, "cis:description") != -1:
            monument_description = info_monument(query_data, "cis:description")
            bot.sendMessage(from_id, monument_description[query_data][0])
        keyboard = []
        keyboard.append(
            InlineKeyboardButton(text="Torna indietro", callback_data=query_data + "/1")
        )
        if check_more_img(query_data) != -1:
            keyboard.append(
                InlineKeyboardButton(
                    text="Più immagini", callback_data=query_data + "/3"
                )
            )
        if info_monument(query_data, "pmo:oldPicture") != -1:
            keyboard.append(
                InlineKeyboardButton(
                    text="foto storiche", callback_data=query_data + "/2"
                )
            )
        if (
            info_monument(query_data, "dbo:lat") != -1
            and info_monument(query_data, "dbo:long") != -1
        ):
            monument_lat = info_monument(query_data, "dbo:lat")
            monument_long = info_monument(query_data, "dbo:long")
            bot.sendLocation(
                from_id,
                monument_lat[query_data][0],
                monument_long[query_data][0],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]),
            )
        return
    # caso in cui è presente uno dei 3 comandi
    command = query_data[query_data.find("/") + 1]
    id = query_data[0 : query_data.find("/")]  # noqa E203
    # print("Comando: {} \n".format(command))
    # print("ID: {} \n".format(id))
    if int(command) == 1:
        # print("Premuto Tasto indietro \n")
        # Nel caso in cui l'utente vuole tornare indietro, non faccio altro che ricreare
        # il pacchetto msg originale inviando id, lat e long e richiamando la funzione
        # send_monument_nearby. Questo perchè è più comodo ricostruire la lista
        # piuttosto che doverla memorizzare per ogni utente la relativa keyboard
        lat = last_positions[from_id][0]
        long = last_positions[from_id][1]
        # lat = info_monument(str(id), "dbo:lat")
        # long = info_monument(str(id), "dbo:long")
        update = {
            "chat": {"id": from_id},
            "location": {"latitude": str(lat), "longitude": str(long)},
        }
        send_monument_nearby(bot, update)
    if int(command) == 2:
        # print("Premuto tasto foto storiche \n")
        if info_monument(str(id), "pmo:oldPicture") != -1:
            old_picture = info_monument(str(id), "pmo:oldPicture")
            for x in range(0, len(old_picture[str(id)]), 1):
                bot.sendPhoto(from_id, old_picture[str(id)][x])
            keyboard = []
            keyboard.append(
                InlineKeyboardButton(
                    text="Torna indietro", callback_data=str(id) + "/1"
                )
            )
            text = "Spero queste immagini siano di tuo gradimento, torna indietro per visualizzare i monumenti nelle vicinanze"
            bot.sendMessage(
                from_id,
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]),
            )
    if int(command) == 3:
        # print("Premuto tasto altro foto \n")
        if info_monument(str(id), "pmo:nearbyCulturalInstituteOrSite") != -1:
            more_picture = info_monument(str(id), "pmo:nearbyCulturalInstituteOrSite")
            id_monuments = list()
            for x in range(0, len(more_picture[str(id)]), 1):
                # print(morePicture[str(id)])
                # print("<" + morePicture[str(id)][x] + ">")
                string = "<" + str(more_picture[str(id)][x]) + ">"
                monument = id_monument(string)
                id_monuments.append(monument[string][0])
            message_info = 1
            for m in id_monuments:
                if info_monument(m, "pmo:picture") != -1:
                    if message_info:
                        bot.sendMessage(
                            from_id,
                            "Ecco alcune immagini dei monumenti vicini a quello selezionato",
                        )
                        message_info = 0
                    monument_name = info_monument(m, "cis:institutionalName")
                    monument_photo = info_monument(m, "pmo:picture")
                    bot.sendMessage(
                        from_id, "*" + monument_name[m][0] + "*", parse_mode="Markdown"
                    )
                    bot.sendPhoto(from_id, monument_photo[m][0])
        keyboard = []
        keyboard.append(
            InlineKeyboardButton(text="Torna indietro", callback_data=str(id) + "/1")
        )
        bot.sendMessage(
            from_id,
            "Spero queste immagini siano di tuo gradimento, clicca per visualizzare i monumenti nelle vicinanze",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]),
        )


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # print("
    #   Tipo messaggio: {} \n Tipo chat: {} \n ID Chat: {} \n"
    #   .format(content_type, chat_type, chat_id)
    # )
    if content_type == "location":
        send_monument_nearby(bot, msg)
    else:
        if msg["text"] == "/start":
            bot.sendMessage(
                chat_id,
                "Benvenuto, mandami la tua posizione per trovare i punti di interesse vicino a te:",
                reply_markup=None,
            )
        elif msg["text"] == "/info":
            bot.sendMessage(
                chat_id,
                "Benvenuto all'interno del bot Guida ai monumenti di Palermo.\nQuesto bot è stato realizzato per permettere ai turisti o semplicemente ai palermitani, di conoscere con maggiore dettaglio i monumenti che li circondano, permettendo in oltre di visionare ove presenti, le immagini storiche del monumento scelto. Banca dati utilizzata per la geolocalizzazione: OpenStreetMap.org (licenza: ODBL).\nInoltre si ringrazia la biblioteca comunale di Palermo per aver reso possibile questo progetto mediante foto messe a disposizione in modo totalmente gratuito all'interno della piattaforma Flickr con username: 'Biblioteca comunale Palermo' a cura della dott.ssa Eliana Calandra.",
                reply_markup=None,
            )
        else:
            bot.sendMessage(
                chat_id, "Comandi disponibili: \n /start \n /info", reply_markup=None
            )


bot = telepot.Bot(os.getenv("TOKEN"))
"""
struttura dati utilizzata solo per ricavare i monumenti vicino alla posizione mandata
dall'utente, cosa non possibile mediante query per problemi dovuti alla geodistance.
"""
monuments = read_monuments()
last_positions = {}


def main():
    MessageLoop(
        bot, {"chat": handle, "callback_query": on_callback_query}
    ).run_as_thread()
    print("In attesa di un messaggio..")
    while 1:
        time.sleep(1)


if __name__ == "__main__":
    main()
