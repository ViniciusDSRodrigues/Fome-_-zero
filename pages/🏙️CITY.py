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
st.header('🏙️ Visão Cidades')
with st.container():
    st.write('### Top 10 cidades com mais restaurantes')
    register_restaurant_per_city = df_final.loc[:, ['city', 'restaurant_id', 'country']].groupby(
        ['city', 'country']).nunique().reset_index()
    register_restaurant_per_city_top10 = register_restaurant_per_city.sort_values(by='restaurant_id',
                                                                                  ascending=False).head(10)
    register_restaurant_per_city_top10.columns = ['Cidade', 'País', "Quantidade de restaurantes"]
    fig = px.bar(register_restaurant_per_city_top10, x='Cidade', y="Quantidade de restaurantes", text="Quantidade de restaurantes",
                 text_auto='.4s', color='País')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis={'tickangle': 45})
    st.plotly_chart(fig, use_container_width=True)
with st.container():
    st.markdown("""---""")
    col1, col2 = st.columns(2)
    with col1:
        st.write('###### Top 7 Cidades com mais restaurantes com nota média acima de 4.5')
        over_four_per_city = df_final.loc[df_final['aggregate_rating'] >= 4.0,
                                          ['restaurant_id', 'city','country']].groupby(['country', 'city']).nunique().reset_index()
        over_four_per_city.columns = ['País', 'Cidade', 'Quantidade']
        over_four_per_city_top7 = over_four_per_city.sort_values(by='Quantidade', ascending=False).head(7)
        fig = px.bar(over_four_per_city_top7, x='Cidade', y="Quantidade", text="Quantidade", text_auto='.2s',
                     color='País')
        fig.update_layout(xaxis={'tickangle': 45})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write('######  Top 7 Cidades com mais restaurantes com nota média abaixo de 2.5')
        under_four_per_city = df_final.loc[df_final['aggregate_rating'] <= 2.5,
                                          ['restaurant_id', 'city', 'country']].groupby(
            ['country', 'city']).nunique().reset_index()
        under_four_per_city.columns = ['País', 'Cidade', 'Quantidade']
        under_four_per_city_top7 = under_four_per_city.sort_values(by='Quantidade', ascending=False).head(7)
        fig = px.bar(under_four_per_city_top7, x='Cidade', y="Quantidade", text="Quantidade", text_auto='.2s',
                     color='País')
        fig.update_layout(xaxis={'tickangle':45})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)
with st.container():
    st.markdown("""---""")
    st.write('### Top 10 cidades com mais tipos de culinárias distintas')
    qtde_cuisines = df_final.loc[:, ['city','cuisines','country']].groupby(['country', 'city']).nunique().reset_index()
    qtde_cuisines.columns = ['País', 'Cidade', 'Quantidade']
    qtde_cuisines.sort_values(by='Quantidade', ascending=False)
    qtde_cuisines_top10 = qtde_cuisines.sort_values(by='Quantidade', ascending=False).head(10)
    fig = px.bar(qtde_cuisines_top10, x='Cidade', y="Quantidade", text="Quantidade",
                 text_auto='.2s', color='País')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis={'tickangle': 45})
    st.plotly_chart(fig, use_container_width=True)

