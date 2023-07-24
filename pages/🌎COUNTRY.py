import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium.plugins
import branca
import branca.colormap as cm
import pandas as pd
import inflection
from haversine import haversine
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
import plotly.express as px


#------------- FUNÇÕES ---------------


#- FUNÇÃO DE RENOMEAR COLUNAS DO DF.

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

#- FUNÇÃO CRIAR COLUNA COM NOME DOS PAÍSES NO DF

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

#- FUNÇÃO CRIAR COLUNA COM CORES A PARTIR DO CÓDIGO DE UMA COLUNA DE CORES DO DF
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

#- FUNÇAO QUE DEFINE PREÇO ATRAVÉS DA COLUNA 'PRICE_RANGE' DO DF
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
#- FUNÇÃO PARA PEGAR PRIMEIRA CULINARIA DAS CELULAS DE CUISINES
def first_cuisine(texto):
    texto = str(texto).split(",")[0]
    return texto

#IMPORTANTO O DF E FAZENDO OS DEVIDOS TRATAMENTOS.
df = pd.read_csv('zomato_data_base.csv')
df_final = rename_columns(df)
df_final = df_final.dropna(how='any')
df_final['country'] = df_final['country_code'].apply(country_name)
df_final['colors'] = df_final['rating_color'].apply(color_name)
df_final['price_category'] = df_final['price_range'].apply(create_price_tye)
df_final["cuisines"] = df_final["cuisines"].apply(first_cuisine)

# -------------------- MAIN PAGE -------------------- #
# =====================================
#            Barra Lateral - PARTE 1
# =====================================
image_path = "data-science_file.png"
image = Image.open(image_path)
st.sidebar.image(image,width=120)

st.sidebar.markdown('## Fome Zero')

country_options = st.sidebar.multiselect('Escolha os Países que deseja visualizar os restaurantes',["India","Australia","Brazil","Canada","Indonesia","New Zeland","Philippines",
"Qatar","Singapure","South Africa","Sri Lanka","Turkey","United Arab Emirates","England","United States of America",],
                       default=['Brazil','England','Qatar','South Africa','Canada','Australia'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("""### Powered by Vinicius Rodrigues""")
## ===== FILTRO DE PAÍS =====
filtro_pais_linhas = df_final['country'].isin(country_options)#a msm lógica do q fzr if 'a' in vanessa: retornar true e ai o filtro será aplicado assim, pois condicional true faz o filtro.
df_final = df_final.loc[filtro_pais_linhas,:]

# =====================================
#        layout no Streamlit
# =====================================
st.header('🌎 Visão países')
with st.container():
    st.write('### Quantidade de restaurantes por país')
    graph_rest_country = df_final.loc[:, ['country', 'restaurant_id']].groupby(['country']).nunique().reset_index()
    graph_rest_country.columns = ['Países', 'Quantidade de Restaurantes']
    graph_rest_country = graph_rest_country.sort_values(by='Quantidade de Restaurantes', ascending=False)
    fig = px.bar(graph_rest_country, x='Países', y='Quantidade de Restaurantes', text='Quantidade de Restaurantes',
                 text_auto='.4s')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)
with st.container():
    st.markdown("""---""")
    st.write('### Quantidade de cidades por país')
    graph_cities_country = df_final.loc[:, ['country', 'city']].groupby(['country']).nunique().reset_index()
    graph_cities_country.columns = ['Países', 'Quantidade de Cidades']
    graph_cities_country = graph_cities_country.sort_values(by='Quantidade de Cidades', ascending=False)
    fig = px.bar(graph_cities_country, x='Países', y='Quantidade de Cidades', text='Quantidade de Cidades', text_auto='.0s')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis={'tickangle': 45})
    st.plotly_chart(fig, use_container_width=True)
with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    with col1:
        col1.markdown('Média de avaliações por país')
        graph_avaliation_country = df_final.loc[:, ['country', 'votes']].groupby(['country']).mean().reset_index()
        graph_avaliation_country.columns = ['País', 'Média de avaliações']
        graph_avaliation_country = graph_avaliation_country.sort_values(by='Média de avaliações', ascending=False)
        fig = px.bar(graph_avaliation_country, x='País', y='Média de avaliações', text='Média de avaliações',
                     text_auto='.4s')
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis={'tickangle': 45})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        col2.markdown('Média de um prato para dois por país')
        graph_price_country = df_final.loc[:, ['country', 'average_cost_for_two']].groupby(
            ['country']).mean().reset_index()
        graph_price_country.columns = ['País', 'Média do valor']
        graph_price_country = graph_price_country.sort_values(by='Média do valor', ascending=False)
        fig = px.bar(graph_price_country, x='País', y='Média do valor', text='Média do valor', text_auto='.4s')
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis={'tickangle': 45})
        st.plotly_chart(fig, use_container_width=True)
with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    with col1:
        col1.markdown('Top 5 restaurantes - categoria de preço gourmet')
        graph_price_categori = df_final.loc[df_final['price_category'] == 'gourmet'
        , ['restaurant_id', 'country']].groupby(['country']).nunique().reset_index()
        graph_price_categori.columns = ['País', 'Quantidade']
        graph_price_categori_top5 = graph_price_categori.sort_values(by='Quantidade', ascending=False).head(5)
        fig = px.bar(graph_price_categori_top5, x='País', y='Quantidade', text='Quantidade', text_auto='.0s')
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis={'tickangle': 45})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        col2.markdown('Top 5 restaurantes - categoria de preço cheap')
        graph_price_categori = df_final.loc[df_final['price_category'] == 'cheap'
        , ['restaurant_id', 'country']].groupby(['country']).nunique().reset_index()
        graph_price_categori.columns = ['País', 'Quantidade']
        graph_price_categori_top5 = graph_price_categori.sort_values(by='Quantidade', ascending=False).head(5)

        fig = px.bar(graph_price_categori_top5, x='País', y='Quantidade', text='Quantidade', text_auto='.0s')
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis={'tickangle': 45})
        st.plotly_chart(fig, use_container_width=True)
