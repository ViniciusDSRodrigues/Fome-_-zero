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

#FILTRO DE PAÍS
country_options = st.sidebar.multiselect('Escolha os Países que deseja visualizar os restaurantes',["India","Australia","Brazil","Canada","Indonesia","New Zeland","Philippines",
"Qatar","Singapure","South Africa","Sri Lanka","Turkey","United Arab Emirates","England","United States of America",],
                       default=['Brazil','England','Qatar','South Africa','Canada','Australia'])

st.sidebar.markdown("""---""")
#FILTRO DE CULINÁRIA
lista_culinaria = [culinaria for culinaria in df_final['cuisines'].unique()]

cuisine_options = st.sidebar.multiselect('Escolha os tipos de culinária',lista_culinaria,
                       default=['Home-made','BBQ','Japanese','Brazilian','Arabian','American','Italian'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("""### Powered by Vinicius Rodrigues""")
## ===== FILTRO DE PAÍS =====
filtro_pais_linhas = df_final['country'].isin(country_options)#a msm lógica do q fzr if 'a' in vanessa: retornar true e ai o filtro será aplicado assim, pois condicional true faz o filtro.
df_final = df_final.loc[filtro_pais_linhas,:]

## ===== FILTRO DE CULINÁRIA =====
filtro_culinaria_linhas = df_final['cuisines'].isin(cuisine_options)
df_final = df_final.loc[filtro_culinaria_linhas]

# =====================================
#        layout no Streamlit
# =====================================
st.header('👨‍🍳 Visão Culinária')
with st.container():
    st.markdown("""--------""")
    st.markdown('### Melhores restaurantes dos principais tipos culinários')
    st.write(
        '<span title="EXEMPLO: NOME DO RESTAURANTE (OUTBACK) : SUA NOTA EM CIMA DA MAIOR POSSÍVEL (3.5/5.0)">🤔</span>',
        unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        col1.markdown(' - Italiana ')
        if not np.any(df_final['cuisines'] == 'Italian'):
            st.write('###### No filtro selecionado, a culinária Italiana não consta.')
        else:
            best_with_italian_food = df_final.loc[
                df_final['cuisines'] == 'Italian', ['restaurant_id', 'aggregate_rating', 'restaurant_name']].groupby(
                ['restaurant_name', 'restaurant_id']).mean().reset_index()
            best_with_italian_food.columns = ['restaurant_name', 'restaurant_id', 'Rating_Mean']
            index_max = best_with_italian_food['Rating_Mean'].idxmax()
            st.write('###### {}: {}/5.0'.format(best_with_italian_food['restaurant_name'][index_max],
                                                 best_with_italian_food['Rating_Mean'][index_max]))
        with col2:
            col2.markdown(' - Americana ')
            if not np.any(df_final['cuisines'] == 'American'):
                st.write('###### No filtro selecionado, a culinária Americana não consta.')
            else:
                best_with_american_food = df_final.loc[
                    df_final['cuisines'] == 'American', ['restaurant_id', 'aggregate_rating', 'restaurant_name']].groupby(
                    ['restaurant_name', 'restaurant_id']).mean().reset_index()
                best_with_american_food.columns = ['restaurant_name', 'restaurant_id', 'Rating_Mean']
                index_max = best_with_american_food['Rating_Mean'].idxmax()
                st.write('###### {}: {}/5.0'.format(best_with_american_food['restaurant_name'][index_max],
                                                    best_with_american_food['Rating_Mean'][index_max]))
        with col3:
            col3.markdown(' - Brasileira ')
            if not np.any(df_final['cuisines'] == 'Brazilian'):
                st.write('###### No filtro selecionado, a culinária Brasileira não consta.')
            else:
                best_with_brazilian_food = df_final.loc[
                    df_final['cuisines'] == 'Brazilian', ['restaurant_id', 'aggregate_rating', 'restaurant_name']].groupby(
                    ['restaurant_name', 'restaurant_id']).mean().reset_index()
                best_with_brazilian_food.columns = ['restaurant_name', 'restaurant_id', 'Rating_Mean']
                index_max = best_with_brazilian_food['Rating_Mean'].idxmax()
                st.write('###### {}: {}/5.0'.format(best_with_brazilian_food['restaurant_name'][index_max],
                                                    best_with_brazilian_food['Rating_Mean'][index_max]))
        with col4:
            col4.markdown(' - Japonesa ')
            if not np.any(df_final['cuisines'] == 'Japanese'):
                st.write('###### No filtro selecionado, a culinária Japonesa não consta.')
            else:
                best_with_japanese_food = df_final.loc[
                    df_final['cuisines'] == 'Japanese', ['restaurant_id', 'aggregate_rating', 'restaurant_name']].groupby(
                    ['restaurant_name', 'restaurant_id']).mean().reset_index()
                best_with_japanese_food.columns = ['restaurant_name', 'restaurant_id', 'Rating_Mean']
                index_max = best_with_japanese_food['Rating_Mean'].idxmax()
                st.write('###### {}: {}/5.0'.format(best_with_japanese_food['restaurant_name'][index_max],
                                                    best_with_japanese_food['Rating_Mean'][index_max]))
        with col5:
            col5.markdown(' - Árabe ')
            if not np.any(df_final['cuisines'] == 'Arabian'):
                st.write('###### No filtro selecionado, a culinária Árabe não consta.')
            else:
                best_with_arabian_food = df_final.loc[
                    df_final['cuisines'] == 'Arabian', ['restaurant_id', 'aggregate_rating', 'restaurant_name']].groupby(
                    ['restaurant_name', 'restaurant_id']).mean().reset_index()
                best_with_arabian_food.columns = ['restaurant_name', 'restaurant_id', 'Rating_Mean']
                index_max = best_with_arabian_food['Rating_Mean'].idxmax()
                st.write('###### {}: {}/5.0'.format(best_with_arabian_food['restaurant_name'][index_max],
                                                    best_with_arabian_food['Rating_Mean'][index_max]))
with st.container():
    st.markdown("""--------""")
    st.write(
        '<span title="POR PADRÃO TOP 10 APRESENTADO, PODENDO SER ALTERADO CONFORME SELEÇÃO.">🤔</span>',
        unsafe_allow_html=True)
    option_selected = st.checkbox("Clique aqui poder mudar a quantidade do ranking de restaurantes")
    numero_selecionado = 10
    if option_selected:
        numero_selecionado = st.selectbox("Selecione o número para aplicar ao filtro:", [1,3,5,7,10])
    st.markdown('### Top {} restaurantes'.format(numero_selecionado))
    top_cuisines = df_final.loc[:,:]
    top_10_cuisines = top_cuisines.sort_values(by='aggregate_rating', ascending=False).head(numero_selecionado)
    top_10_cuisines['restaurant_id'] = top_10_cuisines['restaurant_id'].astype(str)
    st.dataframe(top_10_cuisines, use_container_width=True,hide_index=True)
with st.container():
    st.markdown("""--------""")
    col1,col2 = st.columns(2)
    with col1:
        st.write('##### Top {} melhores tipos de culinárias'.format(numero_selecionado))
        top_cuisines = df_final.loc[:, ['restaurant_id', 'cuisines', 'aggregate_rating']].groupby(
            ['cuisines']).mean().reset_index()
        top_10_cuisines = top_cuisines.sort_values(by='aggregate_rating', ascending=False).head(numero_selecionado)
        top_10_cuisines.columns = ['Culinária','restaurant_id','Nota média']
        fig = px.bar(top_10_cuisines, x='Culinária', y="Nota média", text='Nota média', text_auto='.2s')
        fig.update_layout(xaxis={'tickangle': 45})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write('##### Top {} piores tipos de culinárias'.format(numero_selecionado))
        top_cuisines = df_final.loc[:, ['restaurant_id', 'cuisines', 'aggregate_rating']].groupby(
            ['cuisines']).mean().reset_index()
        top_10_cuisines = top_cuisines.sort_values(by='aggregate_rating', ascending=True).head(numero_selecionado)
        top_10_cuisines.columns = ['Culinária','restaurant_id','Nota média']
        fig = px.bar(top_10_cuisines, x='Culinária', y="Nota média", text='Nota média', text_auto='.2s')
        fig.update_layout(xaxis={'tickangle': 45})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

