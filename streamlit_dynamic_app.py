# flake8: noqa
# ruff: noqa
# pylint: skip-file

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import ast
import re
from collections import Counter


st.set_page_config(page_title="Dashboard de comidas", layout="wide")
st.title("Webcetas - Dashboard de Recetas de Cocina")

import streamlit as st


@st.cache_data
def load_data():
    import pandas as pd
    df = pd.read_csv("data/recipes_df.csv")
    df = df[df.category != "Gastronomía"]
    return df

with st.spinner("Cargando recetas y librerías 🍳"):
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    recipes = load_data()

st.sidebar.title("Navegación")
page = st.sidebar.selectbox("Selecciona una página:", ["Dashboard Categorías", "Análisis de Ingredientes", "Análisis Nutricional"])



if page == "Dashboard Categorías":
# Exploración de categorías y subcategorías
    categories = recipes['category'].unique().tolist()
    subcategories = {}
    for cat in categories:
        subcategories[cat] = [subcat for subcat in recipes[recipes['category'] == cat]['subcategory'].unique()]

    if page == "Dashboard Categorías":
        st.header("Dashboard de Categorías y Subcategorías de Recetas")
        st.info("Explora las recetas por categorías y subcategorías.")
        
        col_seleccion, col_grafico = st.columns([1, 2])
        with col_seleccion:
            st.subheader("🔍 Filtros")

            # Selectbox para categorías
            categorias = ["Ver todas"] + sorted(recipes['category'].unique().tolist())
            categoria_seleccionada = st.selectbox(
                "Elige una categoría:",
                categorias,
                key="cat_select"
            )
            
            # Si se selecciona una categoría específica, mostrar sus subcategorías
            if categoria_seleccionada != "Ver todas":
                recetas_filtradas = recipes[recipes['category'] == categoria_seleccionada]
                subcategorias = ["Todas"] + sorted(recetas_filtradas['subcategory'].unique().tolist())
                
                subcategoria_seleccionada = st.multiselect(
                    f"Subcategorías de {categoria_seleccionada}:",
                    subcategorias,
                    default=["Todas"],
                    key="subcat_select"
                )
                
                # Aplicar filtro de subcategorías si no son "Todas"
                if "Todas" not in subcategoria_seleccionada:
                    recetas_filtradas = recetas_filtradas[
                        recetas_filtradas['subcategory'].isin(subcategoria_seleccionada)
                    ]
            else:
                recetas_filtradas = recipes.copy()
                subcategoria_seleccionada = ["Todas"]
        
        with col_grafico:
            st.subheader("📊 Gráfico de Recetas")

            # Determinar qué gráfico mostrar
            if categoria_seleccionada == "Ver todas":
                # Gráfico de categorías
                datos = recipes['category'].value_counts().reset_index()
                fig = px.bar(
                    datos,
                    x='category',
                    y='count',
                    color ='category',
                    title="Recetas por Categoría",
                    labels={'category': 'Categoría', 'count': 'Número de Recetas'},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
            else:
                # Gráfico de subcategorías
                datos = recetas_filtradas['subcategory'].value_counts().reset_index()
                fig = px.bar(
                    datos,
                    x='subcategory',
                    y='count',
                    color='subcategory',
                    title=f"Recetas en {categoria_seleccionada}",
                    labels={'subcategory': 'Subcategoría', 'count': 'Número de Recetas'}
                )
            
            fig.update_traces(
                texttemplate='%{y}',
                textposition='inside'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_tickangle=-45,
                height=400,
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            
            st.plotly_chart(fig, use_container_width=True)



        col_seleccion, col_grafico = st.columns([1, 2])
        with col_seleccion:
            st.subheader("📊 Gráfico de dificultad")

            df_diff = recipes.fillna({'difficulty': 'Desconocido'}).copy()

            # Definir orden deseado
            difficulty_order = [
                'Dificultad muy baja',
                'Dificultad baja',
                'Dificultad media',
                'Dificultad alta',
                'Dificultad muy alta',
                'Desconocido'
            ]

            # Convertir a categoría con orden
            df_diff['difficulty'] = pd.Categorical(df_diff['difficulty'], categories=difficulty_order, ordered=True)

            if categoria_seleccionada == "Ver todas":
                # Contar dificultades respetando el orden
                datos_diff_count = df_diff['difficulty'].value_counts().reindex(difficulty_order, fill_value=0).reset_index()
                datos_diff_count.columns = ['difficulty', 'count']
                titulo_diff = "Dificultad de Recetas (Todas las categorías)"
            else:
                # Filtrar por categoría
                datos_categoria = df_diff[df_diff['category'] == categoria_seleccionada]

                # Selección opcional de subcategoría
                subcategorias = sorted(datos_categoria['subcategory'].dropna().unique())
                subcategoria_sel_diff = st.selectbox("Subcategoría (Dificultad)", ["Todas"] + subcategorias)
                if subcategoria_sel_diff != "Todas":
                    datos_categoria = datos_categoria[datos_categoria['subcategory'] == subcategoria_sel_diff]

                # Contar dificultades respetando el orden
                datos_diff_count = datos_categoria['difficulty'].value_counts().reindex(difficulty_order, fill_value=0).reset_index()
                datos_diff_count.columns = ['difficulty', 'count']

                titulo_diff = f"Dificultad en {categoria_seleccionada}"
                if subcategoria_sel_diff != "Todas":
                    titulo_diff += f" / {subcategoria_sel_diff}"

            # Crear gráfico
            fig_diff = px.pie(
                datos_diff_count,
                hole=0.4,
                names='difficulty',
                values='count',
                color='difficulty',
                title=titulo_diff,
                color_discrete_map={
                    'Dificultad muy baja': 'lightgreen',
                    'Dificultad baja': 'yellowgreen',
                    'Dificultad media': 'orange',
                    'Dificultad alta': 'red',
                    'Dificultad muy alta': 'darkred',
                    'Desconocido': 'lightgrey'
                },
                category_orders={'difficulty': difficulty_order}
            )

            fig_diff.update_traces(textposition='inside', textinfo='percent+label')
            fig_diff.update_layout(showlegend=False, height=400, margin=dict(t=40, l=10, r=10, b=10),
                                   uniformtext_minsize=8,
                                   uniformtext_mode='hide')
            st.plotly_chart(fig_diff, use_container_width=True)


        with col_grafico:
            st.subheader("📊 Gráfico de tipo de plato por categoría")

            df_tipo = recipes.fillna({'type_of_dish': 'Desconocido'}).copy()
            df_tipo['type_of_dish_clean'] = df_tipo['type_of_dish'].astype(str).str.strip().str.lower()

            if categoria_seleccionada == "Ver todas":
                datos_count = df_tipo['type_of_dish_clean'].value_counts().reset_index()
                datos_count.columns = ['type_of_dish_clean', 'count']
                titulo_tipo = "Número de recetas por Tipo de Plato (Todas las categorías)"
            else:
                datos_categoria = df_tipo[df_tipo['category'] == categoria_seleccionada]
                subcategorias = sorted(datos_categoria['subcategory'].dropna().unique())
                subcategoria_sel_tipo = st.selectbox("Subcategoría (Tipo de Plato)", ["Todas"] + subcategorias)
                if subcategoria_sel_tipo != "Todas":
                    datos_categoria = datos_categoria[datos_categoria['subcategory'] == subcategoria_sel_tipo]
                datos_count = datos_categoria['type_of_dish_clean'].value_counts().reset_index()
                datos_count.columns = ['type_of_dish_clean', 'count']
                titulo_tipo = f"Tipo de Plato en {categoria_seleccionada}"
                if subcategoria_sel_tipo != "Todas":
                    titulo_tipo += f" / {subcategoria_sel_tipo}"

            fig_tipo = px.bar(
                datos_count,
                x='type_of_dish_clean',
                y='count',
                color='type_of_dish_clean',
                title=titulo_tipo,
                labels={'type_of_dish_clean': 'Tipo de Plato', 'count': 'Número de Recetas'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_tipo.update_traces(texttemplate='%{y}', textposition='inside')
            fig_tipo.update_layout(
                showlegend=False,
                xaxis_tickangle=-45,
                height=400,
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.plotly_chart(fig_tipo, use_container_width=True)

 
    st.markdown('---')
    st.header("📋 Observa las recetas en su web")
    
    # Mostrar recetas por categoría (usando tu formato específico)
    for cat in subcategories.keys():
        with st.expander(f"Categoría: {cat}"):
            subcat_options = subcategories[cat]
            selected_subcats = st.multiselect(
                f"Selecciona subcategorías en {cat}:", 
                subcat_options, 
                default=subcat_options,
                key=f"multiselect_{cat}"
            )
            
            filtered_recipes = recipes[
                (recipes['category'] == cat) & 
                (recipes['subcategory'].isin(selected_subcats))
            ]
            filtered_recipes = filtered_recipes.fillna("")
            
            st.write(f"Se encontraron {len(filtered_recipes)} recetas en la categoría '{cat}' con las subcategorías seleccionadas.")
            
            # Filtrar solo las columnas que existen
            available_columns = ['recipe_name', 'subcategory', 'type_of_dish', 'difficulty', 'recipe_url']
            columns_to_show = [col for col in available_columns if col in filtered_recipes.columns]
            
            if columns_to_show:
                df = filtered_recipes[columns_to_show]
                
                # Convertir a Markdown con links si existe recipe_url
                if 'recipe_url' in columns_to_show:
                    md_table = "| Receta | Subcategoría | Tipo | Dificultad |\n|---|---|---|---|\n"
                    for _, row in df.iterrows():
                        recipe_name = row.get('recipe_name', 'Sin nombre')
                        recipe_url = row.get('recipe_url', '')
                        subcategory = row.get('subcategory', '')
                        type_of_dish = row.get('type_of_dish', '')
                        difficulty = row.get('difficulty', '')
                        
                        if recipe_url and recipe_url.strip():
                            md_table += f"| [{recipe_name}]({recipe_url}) | {subcategory} | {type_of_dish} | {difficulty} |\n"
                        else:
                            md_table += f"| {recipe_name} | {subcategory} | {type_of_dish} | {difficulty} |\n"
                    
                    st.markdown(md_table, unsafe_allow_html=True)
                else:
                    # Si no hay URL, mostrar tabla normal
                    st.dataframe(df, use_container_width=True)

    st.markdown("---")



elif page == "Análisis de Ingredientes":
    st.header("Análisis de Ingredientes")
    st.info("Explora los ingredientes más comunes en las recetas.")

    translation_dict = {
        'cebolla': 'onion', 'aceite': 'oil', 'agua': 'water', 'huevo': 'egg',
        'huevos': 'egg', 'leche': 'milk', 'ajo': 'garlic', 'azúcar': 'sugar',
        'mantequilla': 'butter', 'harina': 'flour', 'sal': 'salt', 
        'pimienta': 'pepper', 'limón': 'lemon', 'olive oil': 'oil',
        'teeth of ajo': 'garlic', 'dientes de ajo': 'garlic',
        'garlic teeth': 'garlic','garlic tooth': 'garlic' ,'cucharada de aceite': 'oil',
        'chicken breast': 'chicken', 'pechuga de pollo': 'chicken',
        'wheat flour': 'flour', 'all-purpose flour': 'flour',
    }

        # Selector para mostrar ingredientes por categoría o general
    categoria_ingredientes = st.selectbox(
        "Mostrar ingredientes de:",
        ["General"] + sorted(recipes['category'].unique().tolist())
    )

    # Filtrar recetas según la categoría seleccionada
    if categoria_ingredientes == "General":
        df_ingredientes_filtrado = recipes
    else:
        df_ingredientes_filtrado = recipes[recipes['category'] == categoria_ingredientes]

    # Extraer todos los ingredientes del dataframe filtrado
    all_ingredients_filtrado = []
    for ing_list in df_ingredientes_filtrado['ingredients_list'].dropna():
        for ing in ing_list.split(', '):
            if not isinstance(ing, str):
                continue
            ing_clean = ing.lower().strip()
            ing_clean = re.sub(r'[^a-z\s]', '', ing_clean)
            ing_clean = ing_clean.replace("jet of", "").replace("to taste", "").replace("extra virgin", "").strip()
            if ing_clean.endswith('s') and len(ing_clean) > 3:
                ing_clean = ing_clean[:-1]
            ing_clean = translation_dict.get(ing_clean, ing_clean)
            if ing_clean:
                all_ingredients_filtrado.append(ing_clean)

    # Contar frecuencia y tomar top 10
    ingredientes_df = pd.DataFrame({'Ingrediente': all_ingredients_filtrado})
    ingredientes_df = ingredientes_df.value_counts().reset_index(name='Cantidad').head(10)

    # Gráfico
    fig_ingredientes = px.bar(
        ingredientes_df,
        x='Ingrediente',
        y='Cantidad',
        text="Cantidad",
        title=f"Top 10 Ingredientes - {categoria_ingredientes}",
        labels={'Ingrediente': 'Ingrediente', 'Cantidad': 'Número de Apariciones'},
        color='Cantidad',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_ingredientes.update_traces(textposition="inside")

    fig_ingredientes.update_layout(xaxis_tickangle=-90  , height=500,
                                   uniformtext_minsize=8,
                                   uniformtext_mode='hide')
    st.plotly_chart(fig_ingredientes, use_container_width=True)


    # Explorador de recetas y sus alergias asociadas:
    st.title("Alérgenos por categoría")

    # Limpiar alérgenos:

    def clean_allergen_entry(entry):
        
        if entry is None or entry == "" or entry == "[]":
            return []
        
        # Si ya es lista real
        if isinstance(entry, list):
            return [str(x).strip().replace("'", "").replace("[", "").replace("]", "") for x in entry]
        
        # Si parece lista en texto: ['Gluten', 'Milk']
        if isinstance(entry, str) and entry.strip().startswith("[") and entry.strip().endswith("]"):
            try:
                parsed = ast.literal_eval(entry)
                return [str(x).strip() for x in parsed]
            except:
                pass
        
        # Si es string con comas
        if isinstance(entry, str):
            return [x.strip().replace("'", "") for x in entry.split(",") if x.strip()]
        
        return []

    categoria = st.selectbox(
        "Categoría",
        ["Todas"] + sorted(recipes["category"].unique())
    )

    # Si categoría = Todas → no mostrar subcategoría
    if categoria == "Todas":
        filtro_cat = recipes
        subcategoria = "Todas"
    else:
        filtro_cat = recipes[recipes["category"] == categoria]
        subcats = filtro_cat["subcategory"].unique()
        subcategoria = st.selectbox("Subcategoría", sorted(subcats))

    view = st.radio("Vista", ["Diagrama de Sol", "Histograma"], horizontal=True)


    if subcategoria == "Todas":
        filtro = filtro_cat
    else:
        filtro = filtro_cat[filtro_cat["subcategory"] == subcategoria]


    # Usar SIEMPRE la función de limpieza
    todos_alergenos = []
    for row in filtro["detected_allergies"]:
        todos_alergenos.extend(clean_allergen_entry(row))

    conteo = Counter(todos_alergenos)
    
    def plot_sunburst_counter(counter):
        df = pd.DataFrame({
            "parent": [f"{categoria} - {subcategoria}"] * len(counter),
            "alergeno": list(counter.keys()),
            "freq": list(counter.values())
        })

        root = pd.DataFrame({
        "parent": [""],
        "alergeno": [f"{categoria} - {subcategoria}"],
        "freq": [sum(counter.values())]
    })
        df_full = pd.concat([root, df], ignore_index=True)

        fig = px.sunburst(
            df_full,
            names="alergeno",
            parents="parent",
            values="freq",
            color="freq",
            color_continuous_scale=px.colors.sequential.Reds,
            title="Sunburst de alérgenos"
        )
        fig.update_layout(margin=dict(t=40, l=10, r=10, b=10), height=600)
        return fig
    
    def plot_hist(counter):
    # Convertir a lista ordenada por frecuencia descendente
        data = sorted(
            [{"alergeno": k, "freq": v} for k, v in counter.items()],
            key=lambda x: -x["freq"]
        )

        # Crear gráfico ordenado + colores
        fig = px.bar(
            data,
            x="alergeno",
            y="freq",
            text="freq",
            color="freq",  # colores según frecuencia
            color_continuous_scale=px.colors.sequential.Reds
        )

        fig.update_traces(textposition="inside")

        fig.update_layout(
            height=500,
            xaxis_title="Alergeno",
            yaxis_title="Frecuencia",
            xaxis=dict(categoryorder='array', categoryarray=[d["alergeno"] for d in data]),
            margin=dict(l=10, r=10, t=10, b=80),
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )
        return fig


    if view == "Diagrama de Sol":
        st.plotly_chart(plot_sunburst_counter(conteo), use_container_width=True)
    else:
        st.plotly_chart(plot_hist(conteo), use_container_width=True)

    # Buscador de recetas por ingredientes


    st.subheader("🔍 Buscar recetas por ingredientes y alergias")

    # Alergias:
    recipes['detected_allergies'] = recipes['detected_allergies'].apply(clean_allergen_entry)

    # Construir lista de alergias únicas
    all_allergies = sorted(set(a for sublist in recipes['detected_allergies'] for a in sublist))

    selected_allergies = st.multiselect(
        "Excluir recetas con estas alergias (Sujeto a errores por mala detección de ingredientes):",
        all_allergies,
        default=[],
        help="Selecciona alergias a excluir"
    )

    # Contar todos los ingredientes y ordenarlos
    ingrediente_counts_total = pd.Series(all_ingredients_filtrado).value_counts()

    # Lista de ingredientes única, ordenada por frecuencia descendente
    sorted_ingredients = ingrediente_counts_total.index.tolist()

    # Multiselect con scroll y búsqueda
    selected_ingredients = st.multiselect(
        "Selecciona ingredientes (aparecen ingredientes relacionados - sujeto a errores):",
        sorted_ingredients,
        default=[],
        help="Escribe para buscar o selecciona de la lista"
    )

    if selected_ingredients:
        def recipe_contains_ingredients(ingredient_list, selected):
            if not isinstance(ingredient_list, str):
                return False
            recipe_ings = [
                i.lower().replace("[","").replace("]","").replace("'","").strip()
                for i in ingredient_list.split(', ')
            ]
            recipe_ings = [
                translation_dict.get(i[:-1] if i.endswith("s") and len(i)>3 else i, i)
                for i in recipe_ings
            ]
            return all(any(sel.lower() in ing for ing in recipe_ings) for sel in selected)

        def has_allergy(recipe_allergies, excluded):
            if isinstance(recipe_allergies, list):
                return any(a in recipe_allergies for a in excluded)
            elif isinstance(recipe_allergies, str):
                recipe_allergies_list = [x.strip().replace("[","").replace("]","").replace("'","") for x in recipe_allergies.split(",")]
                return any(a in recipe_allergies_list for a in excluded)
            return False

        # Barra de progreso
        progress_bar = st.progress(0)
        total_recipes = len(recipes)

        mask = []
        for i, row in enumerate(recipes.itertuples()):
            include = recipe_contains_ingredients(row.ingredients_list, selected_ingredients)
            if include and selected_allergies:
                include = not has_allergy(row.detected_allergies, selected_allergies)
            mask.append(include)
            progress_bar.progress((i + 1) / total_recipes)

        filtered_recipes = recipes[pd.Series(mask, index=recipes.index)]
        progress_bar.empty()
        st.write(f"Se encontraron {len(filtered_recipes)} recetas con los ingredientes seleccionados.")


        with st.spinner("Generando tabla de recetas, por favor espera..."):

            display_columns = ['recipe_name', 'category', 'subcategory', 'type_of_dish', 'difficulty', 'recipe_url']
            df_display = filtered_recipes[display_columns].fillna("")

            md_table = "| Receta | Categoría | Subcategoría | Tipo | Dificultad |\n|---|---|---|---|---|\n"
            progress_bar_2 = st.progress(0)
            total_display = len(df_display)
            for i, (_, row) in enumerate(df_display.iterrows()):
                name, url, category, subcat, type_dish, diff = row['recipe_name'], row['recipe_url'], row['category'], row['subcategory'], row['type_of_dish'], row['difficulty']
                md_table += f"| [{name}]({url}) | {category} | {subcat} | {type_dish} | {diff} |\n"
                progress_bar_2.progress((i + 1) / total_display)

            progress_bar_2.empty()
            st.write("### Recetas encontradas:")
            st.markdown(md_table, unsafe_allow_html=True)
    else:
        st.info("Selecciona al menos un ingrediente para filtrar recetas.")


if page == "Análisis Nutricional":
    st.header("Análisis Nutricional de Recetas")
    st.info("Explora el contenido nutricional de las recetas.")

    nutritional_criteria = ["Calorías", "Fibra", "Proteínas", "Grasas", "Carbohidratos"]
    view_nutritional = st.radio("¿Qué información nutricional buscas?", nutritional_criteria, horizontal=True)

    if view_nutritional:
        criterio_seleccionado = view_nutritional
        nutritional = recipes.copy()

        nutritional = nutritional.dropna(subset=["people_served"])
        upper_quantile_99 = nutritional[criterio_seleccionado].quantile(0.99)
        nutritional[criterio_seleccionado] = nutritional[criterio_seleccionado].clip(upper=upper_quantile_99)

        fig_boxplot = px.box(
            nutritional,
            x=criterio_seleccionado,
            y='category',
            title=f"Distribución de {criterio_seleccionado} por Categoría (sin outliers extremos)",
            labels={criterio_seleccionado: criterio_seleccionado, 'category': 'Categoría'},
            orientation='h',
            color='category',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig_boxplot.update_traces(
            marker=dict(size=3),
            jitter=0.3,
            pointpos=0,
            opacity=0.7,
            boxmean=True,
        )

        fig_boxplot.update_layout(
            height=550,
            xaxis=dict(
                title=criterio_seleccionado,
                range=[0, upper_quantile_99+upper_quantile_99.mean()*0.1],
                showgrid=True
            ),
            yaxis=dict(
                title='Categoría',
                showgrid=False
            ),
            margin=dict(t=60, l=80, r=20, b=40),
            showlegend=False
        )

        st.plotly_chart(fig_boxplot, use_container_width=True)

    st.markdown("---")

    st.subheader("Distribución de criterios nutricionales")
    nutritional = recipes.copy()
    nutritional = nutritional.dropna(subset=["people_served"])


    categories = nutritional['category'].unique().tolist()
    categories.append("Todas")
    category_selected = st.selectbox("Selecciona categoría:", categories)

    if category_selected != "Todas":
        df_plot = nutritional[nutritional['category'] == category_selected]
    else:
        df_plot = nutritional.copy()

    nutrients = ['Grasas','Carbohidratos','Proteínas','Fibra']

    # Filtrar 2.5%-97.5%
    df_filtered = pd.DataFrame()
    for nutrient in nutrients:
        vals = df_plot[nutrient].dropna()
        lower = vals.quantile(0.0)
        upper = vals.quantile(0.95)
        df_filtered[nutrient] = vals[(vals >= lower) & (vals <= upper)]

    # Crear distplot
    fig = ff.create_distplot(
        [df_filtered[n].dropna() for n in nutrients],
        nutrients,
        bin_size=1,
        show_hist=False,
        show_rug=False,
        colors=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        title="Distribución de nutrientes (g) - 95% de los valores",
        xaxis_title="Gramos",
        yaxis_title="Densidad",
        height=500
    )

    fig.update_yaxes(showticklabels=False)

    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")

    st.subheader("Comparador de recetas con diagramas de araña")


    norm_df = nutritional.copy()
    for col in nutritional_criteria:
        norm_df[col] = (nutritional[col] - nutritional[col].min()) / (nutritional[col].max() - nutritional[col].min())


    norm_df.fillna(0, inplace=True)
    cats = nutritional['category'].unique().tolist()

    col1, col2 = st.columns(2)

    cat1 = col1.selectbox("Categoría 1", cats, index=0)
    cat2 = col2.selectbox("Categoría 2", cats, index=1)


    def radar_for_categories(cat1, cat2):

        row1 = norm_df[norm_df['category'] == cat1][nutritional_criteria].mean()
        row2 = norm_df[norm_df['category'] == cat2][nutritional_criteria].mean()

        r1_original = nutritional[nutritional['category'] == cat1][nutritional_criteria].mean().values.tolist()
        r1_original.append(r1_original[0])

        r2_original = nutritional[nutritional['category'] == cat2][nutritional_criteria].mean().values.tolist()
        r2_original.append(r2_original[0])

        r1 = row1.values.tolist()
        r1.append(r1[0])  # cierre

        r2 = row2.values.tolist()
        r2.append(r2[0])  # cierre

        theta_nut_criteria = nutritional_criteria + [nutritional_criteria[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=r1,
            theta=theta_nut_criteria,
            fill='toself',
            name=cat1,
            opacity=0.6,
            fillcolor= '#A3D12E',
            line_color= '#6B8E1A',
            customdata=r1_original,
            hovertemplate=[
            f"{t}: {v:.1f} {'kcal' if t=='Calorías' else 'g'}<br>Categoría: {cat1}"
            for t, v in zip(theta_nut_criteria, r1_original + [r1_original[0]])
            ]
        ))

        fig.add_trace(go.Scatterpolar(
            r=r2,
            theta=theta_nut_criteria,
            fill='toself',
            name=cat2,
            opacity=0.6,
            fillcolor= '#5C2ED1',
            line_color= '#3A1A9B',
            customdata=r2_original,
            hoverinfo='text',
            hovertemplate=[
            f"{t}: {v:.1f} {'kcal' if t=='Calorías' else 'g'}<br>Categoría: {cat2}"
            for t, v in zip(theta_nut_criteria, r2_original + [r2_original[0]])
            ]
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,max(row1.max(), row2.max())*1.1],
                                showticklabels=False,)

            ),
            showlegend=True,
            title=f"Comparación Nutricional: {cat1.upper()} vs {cat2.upper()}",
            height=600,
            margin=dict(t=80, l=80, r=80, b=80)
        )
        return fig





    cats = nutritional['category'].unique().tolist()

    fig = go.Figure()

    # r y theta inicial (primer par de categorías)
    fig = radar_for_categories(cat1, cat2)

    st.plotly_chart(fig, use_container_width=True)
