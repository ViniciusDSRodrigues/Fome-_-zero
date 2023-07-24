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

st.set_page_config(
    page_title="Página Principal",
    page_icon="📊"
)


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

# =====================================
#        layout no Streamlit
# =====================================
st.header('Fome zero!')
st.markdown('## O melhor lugar para encontrar o seu mais novo restaurante favorito!')

with st.container():
    st.markdown("""--------""")
    st.markdown('### Aqui estão algumas informações importantes:')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        restaurant_unique = len(df_final['restaurant_id'].unique())
        col1.markdown('Quantidade de Restaurantes')
        st.write('### {}'.format(restaurant_unique))
    with col2:
        countries = len(df_final['country'].unique())
        col2.markdown('Quantidade de países')
        st.write('### {}'.format(countries))
    with col3:
        cities = len(df_final['city'].unique())
        col3.markdown('Quantidade de cidades')
        st.write('### {}'.format(cities))
    with col4:
        qtde_avalations = '{:,.0f}'.format(df_final['votes'].sum()).replace(',','_').replace('.',',').replace('_','.')
        col4.markdown('Quantidade de avaliações feitas')
        st.write('### {}'.format(qtde_avalations))
    with col5:
        qtde_cuisines = len(df_final['cuisines'].unique())
        col5.markdown('Quantidade de culinárias distintas')
        st.write('### {}'.format(qtde_cuisines))


## ===== FILTRO DE PAÍS ===== *aplicado agr p n interferir nas infos gerais acima do site.
filtro_pais_linhas = df_final['country'].isin(country_options)#a msm lógica do q fzr if 'a' in vanessa: retornar true e ai o filtro será aplicado assim, pois condicional true faz o filtro.
df_final = df_final.loc[filtro_pais_linhas,:]
with st.container():
    st.markdown("""--------""")
    # Criando legenda p grafico de mapa:
    legenda_html = '''
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; background-color: white;
                    padding: 1px; border: 2px solid grey; font-size: 8px; line-height: 0.4;">

            <p><strong> - Legenda:</strong></p>
    '''
    cores = {
        'darkgreen': 'Ótima avaliação',
        'green': 'Avaliação muito boa',
        'lightgreen': 'Avaliação Boa',
        'orange': 'Avaliação média',
        'red': 'Avaliação Ruim',
        'darkred': 'Avaliação Muito ruim',
    }
    for cor, descricao in cores.items():
        legenda_html += f'<p><span style="background-color:{cor}; display: inline-block; width: 12px; height: 12px; margin-right: 5px;"></span>{descricao}</p>'
        legenda_html += '</div>'

    # criando gráfico de mapa e sua base.

    mapa = folium.Map()
    marker_cluster = MarkerCluster().add_to(mapa)
    base_info = ['restaurant_id', 'country', 'longitude', 'latitude', 'colors', 'restaurant_name']
    base_graph_map = df_final[['country', 'longitude', 'latitude', 'colors', 'restaurant_name', 'rating_text']
    ].value_counts().reset_index()

    # Incorpora a legenda personalizada no mapa
    mapa.get_root().html.add_child(folium.Element(legenda_html))
    # cria as infos dos mapas
    for index, info in base_graph_map.iterrows():
        folium.Marker((info['latitude'], info['longitude']),tooltip=str(
                info['restaurant_name']),
                      icon=folium.Icon(info['colors']), popup=(
                    '<strong> Restaurant Name:</strong>' + str(
                info['restaurant_name'] + '\n' + ' ' + '<strong> Avaliation: </strong>' + str(info['rating_text'])))
                      ).add_to(marker_cluster)

    folium_static(mapa)
# =====================================
#            Barra Lateral - PARTE 2
# =====================================
st.sidebar.write("""## Baixe um df com os filtros aplicados""")
st.sidebar.download_button(
        label="Download DataFrame",
        data=df_final.to_csv().encode('utf-8'),  # Converte o DataFrame para CSV e codifica em utf-8
        file_name='df.csv',
        mime='text/csv'
    )
st.sidebar.markdown("""---""")
st.sidebar.markdown("""### Powered by Vinicius Rodrigues""")
