import investpy
import pandas as pd


noticia = investpy.news.economic_calendar(time_zone = None, time_filter = 'time_only' , countries = ['África do Sul', 'Austrália','França','Índia', 'Itália','Japão', 'México', 'Nova Zelândia','Zona Euro','Alemanha','Argentina','Brasil','Canadá','China','Cingapura','Espanha','EUA','Hong Kong','Indonésia','Portugal',' Reino Unido','Suíça'], from_date = '19/04/2020', to_date = '21/04/2020', importances = ['low','medium','high'], categories = None)

noticia.head(441)
excel = pd.ExcelWriter('Noticias.xlsx', engine='xlsxwriter')
noticia.to_excel(excel)
excel.save()