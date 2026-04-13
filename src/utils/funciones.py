"""
funciones.py
Funciones auxiliares para el EDA de Subastas BOE
"""

import pandas as pd
import numpy as np
import re
#-----------------------------------------------------
# -------------       LIMPIEZA     -------------------
#-----------------------------------------------------
def limpiar_importe(texto):
    """
    Convierte texto de importe español a float.
    '55.110,30 €' → 55110.30
    'Sin puja mínima' → None
    """
    #Si esta vacio o encuentra la palabra 'sin' o 'ver' (re.I ingnora mayusculas/minusculas)
    if not texto or re.search(r'sin|ver ', texto, re.I): 
        return None
    
    #Reemplazar cualquier caracter que no sea digito ni coma por ' '
    limpio = re.sub(r'[^\d,]', '', texto)   # queda '55110,30'
    if not limpio:
        return None
    return float(limpio.replace(',', '.'))


def limpiar_dataframe(df):
    """
    Aplica limpieza completa al DataFrame crudo del scraping:
    - Elimina columnas duplicadas
    - Elimina columnas que no aportan
    - Convierte fechas a datetime
    Devuelve el DataFrame limpio.
    """
    df = df.copy()

    # Indicando columnas duplicadas e innecesarias
    cols_eliminar = [
        'id_sub',                   # idéntica a 'referencia' 
        'referencia_det',           # idéntica a 'referencia'
        'num_lotes_listado',        # idéntica a 'lotes'
        'url_detalle',              # URL no aporta al análisis   
        'anuncio_boe',              # código interno del BOE no aporta al análisis 
        'cantidad_reclamada_eur',   # Esta columna solo aplica a subastas judiciales
        'descripcion',              # Esta columna contiene descripcion, mucho texto y no aporta al análisis             
        'fecha_conclusion_listado', # duplicada en formato sucio '01/12/2025 a las 18:00:00' (texto con hora)
        'forma_adjudicacion',       #con 85% registros nulos que no aportan      
        'expediente',               #con 23% registros nulos que no aportan 
        'cuenta_expediente',  #     #con 23% registros nulos que no aportan 
    ]
    #====== Solo eliminar las que existan en el df =======
    cols_eliminar = [c for c in cols_eliminar if c in df.columns]
    df = df.drop(columns=cols_eliminar)

    #==== Fechas a tipo datetime=======
    df['fecha_inicio']= pd.to_datetime(df['fecha_inicio'], errors= 'coerce') #coerce --> si no puede convertir un valor a fecha pone NaT
    df['fecha_conclusion']= pd.to_datetime(df['fecha_conclusion'], errors= 'coerce')
  
    return [df.reset_index(drop=True),cols_eliminar]

def calcular_pct(df):
    """
    Calcula y añade nueva columna descuento_pct
    Devuelve:
     - el DataFrame con las nuevas columnas
     - maskara (tasacion_eur & valor_subasta_eur & tasacion_eur) > 0
    """
    #============= Calcular descuento_pct ==============
    # Mascara para obtener registros que tengan los 3 campos datos mayores a 0 
    mask = (
        df['tasacion_eur'].notna() &
        df['valor_subasta_eur'].notna() &
        (df['tasacion_eur'] > 0)
    )

    # Crea la columna descuento_pct con los datos calculados
    df.loc[mask, 'descuento_pct'] = (
        (df.loc[mask, 'tasacion_eur'] - df.loc[mask, 'valor_subasta_eur'])
        / df.loc[mask, 'tasacion_eur'] * 100
    ).round(2)

    return [df.reset_index(drop = True), mask]

def calcular_duracion_dias(df):
    """
    Calcula y añade nueva columna duracion_dias
    Devuelve:
     - el DataFrame con las nuevas columnas
     - maskara (tasacion_eur & valor_subasta_eur & tasacion_eur) > 0
    """
    # ============ Calcular duración en días ===========
    mask_fechas = df['fecha_inicio'].notna() & df['fecha_conclusion'].notna()
    
    df.loc[mask_fechas, 'duracion_dias'] = (
        df.loc[mask_fechas, 'fecha_conclusion'] -
        df.loc[mask_fechas, 'fecha_inicio']
    ).dt.days

    return df.reset_index(drop = True)

def filtrar_tributarios(df):
    """
    Filtra solo registros de organismos tributarios (AEAT y Recaudación)
    con datos económicos completos y válidos.
    """
    df_filtrado = df[
        df['tipo_subasta'].isin(['AGENCIA TRIBUTARIA', 'RECAUDACIÓN TRIBUTARIA']) &
        df['tasacion_eur'].notna() &
        df['valor_subasta_eur'].notna() &
        (df['tasacion_eur'] > 0) &
        (df['valor_subasta_eur'] > 0) &
        (df['tasacion_eur'] > df['valor_subasta_eur'])
    ].copy()

    return df_filtrado.reset_index(drop=True)

#-------------------------------------------------------
# -------------  RESUMEN DATASET  -------------------
#-------------------------------------------------------

def resumen_dataset(df):
    """Imprime un resumen del dataset"""
    print('===== RESUMEN DEL DATASET =====')
    print(f'Filas   : {df.shape[0]:,}')
    print(f'Columnas: {df.shape[1]}')
    print(f'\n Tipos de subasta:')
    print(df['tipo_subasta'].value_counts().to_string())


    if 'descuento_pct' in df.columns:
        print(f'\n  Descuento sobre tasación (%):')
        print(df['descuento_pct'].describe().round(2))
    print('---------------------------' )

#-------------------------------------------------------
# -------------  TEMA VISUAL GLOBAL  -------------------
#-------------------------------------------------------

import matplotlib.pyplot as plt
import seaborn as sns

# Paleta de colores del proyecto
paleta = ['#2C3E50', "#E74C3C", '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
color_principal = '#2C3E50'   # azul oscuro
color_secundario = '#E74C3C'  # rojo
color_acento = '#3498DB'      # azul claro

def set_tema():
    """
    Aplica el tema visual global a todos los gráficos.
    Llamar una vez al inicio del notebook.
    """
    sns.set_theme(style='whitegrid')
    plt.rcParams.update({
        'figure.figsize'     : (12, 5),
        'figure.dpi'         : 120,
        'axes.titlesize'     : 14,
        'axes.titleweight'   : 'bold',
        'axes.labelsize'     : 12,
        'xtick.labelsize'    : 10,
        'ytick.labelsize'    : 10,
        'axes.spines.top'    : False,
        'axes.spines.right'  : False,
        'figure.facecolor'   : 'white',
        'axes.facecolor'     : '#F8F9FA',
    })
    print(' ==== Tema visual aplicado ====')


#-------------------------------------------------------
# -------------  ANÁLISIS UNIVARIANTE ------------------
#-------------------------------------------------------
def plot_distribucion_descuento(df):
    """
    Histograma + KDE y Boxplot del descuento_pct.
    Muestra líneas de referencia en 25%, 50% y 75%.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # === Histograma con KDE === 
    sns.histplot(
        data=df, x='descuento_pct',
        bins=30, kde=True,
        color=color_principal,
        ax=axes[0]
    )
    # Líneas de referencia
    for val, label, color in [
        (25,  '25%',                      color_acento),
        (50,  '50% — umbral hipótesis',   color_secundario),
        (75,  '75%',                      '#2ECC71'),
    ]:
        axes[0].axvline(
            val, color=color, linestyle='--',
            linewidth=1.5, label=label
        )
    mediana = df['descuento_pct'].median()
    axes[0].axvline(
        mediana, color='black', linestyle='-',
        linewidth=2, label=f'Mediana: {mediana:.1f}%'
    )
    axes[0].set_title('Distribución del descuento sobre tasación')
    axes[0].set_xlabel('Descuento (%)')
    axes[0].set_ylabel('Frecuencia')
    axes[0].legend(fontsize=9)

    # === Boxplot ===
    sns.boxplot(
        data = df, x='descuento_pct',
        color = color_principal,
        flierprops=dict(marker='o', color = color_secundario,
                        markersize=5, alpha=0.6),
        ax=axes[1]
    )
    axes[1].axvline(
        50, color = color_secundario, linestyle='--',
        linewidth=1.5, label='Umbral 50%'
    )
    axes[1].set_title('Boxplot del descuento sobre tasación')
    axes[1].set_xlabel('Descuento (%)')
    axes[1].legend(fontsize=9)

    plt.suptitle(
        'Análisis univariante — Descuento sobre tasación (%)',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.show()


def plot_distribucion_valores(df):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for i, (col, titulo, color) in enumerate([
        ('valor_subasta_eur', 'Valor de subasta (€)', color_acento),
        ('tasacion_eur',      'Tasación (€)',          color_principal),
    ]):
        # Histograma con escala logarítmica
        sns.histplot(
            data=df, x=col,
            bins=30, kde=True,
            color=color,
            log_scale=True,      # ← escala logarítmica
            ax=axes[i, 0]
        )
        media   = df[col].median()
        axes[i, 0].axvline(
            media, color=color_principal, linestyle='--',
            linewidth=1.5, label=f'Mediana: {media:,.0f}€' #:,.0f da un formato
        )
        axes[i, 0].set_title(f'Distribución — {titulo} (escala log)')
        axes[i, 0].set_xlabel(titulo)
        axes[i, 0].set_ylabel('Frecuencia')
        axes[i, 0].legend(fontsize=9)

        # Boxplot con escala logarítmica
        sns.boxplot(
            data=df, x=col,
            color=color,
            flierprops=dict(marker='o', color=color_principal,
                            markersize=4, alpha=0.5),
            ax=axes[i, 1]
        )
        axes[i, 1].set_xscale('log')   # ← escala logarítmica
        axes[i, 1].set_title(f'Boxplot — {titulo} (escala log)')
        axes[i, 1].set_xlabel(titulo)

    plt.suptitle(
        'Análisis univariante — Valores económicos (escala logarítmica)',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.show()


def plot_tipo_subasta(df):
    """
    Barplot horizontal de subastas por tipo con porcentaje.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    conteo = df['tipo_subasta'].value_counts()
    colores = [color_principal, color_secundario]

    # === Barplot horizontal ===
    conteo_df = conteo.reset_index()
    conteo_df.columns = ['tipo_subasta', 'cantidad']

    bars = axes[0].barh(
        conteo_df['tipo_subasta'],
        conteo_df['cantidad'],
        color=colores[:len(conteo)]
    )
    # Etiquetas
    for bar, val in zip(bars, conteo.values):
        axes[0].text(
            val + 2, bar.get_y() + bar.get_height()/2,
            f'{val} subastas ({val/len(df)*100:.1f}%)',
            va='center', fontsize=11
        )
    axes[0].set_title('Número de subastas por tipo')
    axes[0].set_xlabel('Número de subastas')
    axes[0].set_xlim(0, conteo.max() * 1.35)
    axes[0].invert_yaxis()

    # === Pie chart ===
    axes[1].pie(
        conteo.values,
        labels=conteo.index,
        colors=colores[:len(conteo)],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11}
    )
    axes[1].set_title('Proporción por tipo de organismo')

    plt.suptitle(
        'Análisis univariante — Tipo de subasta',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.show()

#-------------------------------------------------------
# -------------  ANÁLISIS BIVARIANTE  ------------------
#-------------------------------------------------------

def plot_descuento_por_tipo(df):
    """
    Boxplot y barplot del descuento_pct por tipo de subasta.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # ===== Boxplot === 
    sns.boxplot(
        data=df, x='tipo_subasta', y='descuento_pct',
        palette=[color_principal, color_acento], 
        hue= 'tipo_subasta', legend= False,
        ax=axes[0]
    )
    axes[0].axhline(50, color=color_secundario, linestyle='--',
                    linewidth=1.5, label='Umbral 50%')
    axes[0].set_title('Descuento por tipo de subasta')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Descuento (%)')
    axes[0].legend()  # Leyenda manual para el 'Umbral 50%'

    # ==== Barplot media === 
    media = df.groupby('tipo_subasta')['descuento_pct'].mean().reset_index()
    bars = axes[1].bar(
        media['tipo_subasta'], media['descuento_pct'],
        color=[color_principal, color_acento]
    )
    axes[1].axhline(50, color= color_secundario, linestyle='--',
                    linewidth=1.5, label='Umbral 50%')
    for bar, val in zip(bars, media['descuento_pct']):
        axes[1].text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=12
        )
    axes[1].set_title('Descuento medio por tipo de subasta')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Descuento medio (%)')
    axes[1].legend()

    plt.suptitle(
        'Análisis bivariante — Descuento por tipo de subasta',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.show()

def plot_valor_vs_tasacion(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    colores_tipo = {
        'AGENCIA TRIBUTARIA'    : color_principal,
        'RECAUDACIÓN TRIBUTARIA': color_secundario
    }

    for tipo, grupo in df.groupby('tipo_subasta'):
        ax.scatter(
            grupo['tasacion_eur'],
            grupo['valor_subasta_eur'],
            color=colores_tipo.get(tipo, color_acento),
            label=tipo, alpha=0.6, s=40
        )

    # Línea donde valor = tasacion
    max_val = max(df['tasacion_eur'].max(), df['valor_subasta_eur'].max()) #valor maximo de las 2 columnas
    ax.plot(
        [0, max_val], [0, max_val],
        color='black', linestyle='--',
        linewidth=1.5, label='Valor = Tasación'
    )

    # Escala logarítmica en ambos ejes
    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_title('Valor de subasta vs Tasación (escala logarítmica)')
    ax.set_xlabel('Tasación (€) — escala log')
    ax.set_ylabel('Valor de subasta (€) — escala log')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_evolucion_mensual(df):
    """
    Evolución de subastas y descuento medio por mes.
    """
    df = df.copy()
    df['mes'] = df['fecha_conclusion'].dt.to_period('M').astype(str)

    resumen = df.groupby('mes').agg(
        num_subastas    = ('referencia', 'count'),
        descuento_medio = ('descuento_pct', 'mean')
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Nº subastas por mes
    bars1 = axes[0].bar(
        resumen['mes'], resumen['num_subastas'],
        color= color_principal
    )
    for bar in bars1:
        axes[0].text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 1,
            str(int(bar.get_height())),
            ha='center', va='bottom', fontsize=12
        )
    axes[0].set_title('Número de subastas por mes')
    axes[0].set_xlabel('Mes')
    axes[0].set_ylabel('Nº subastas')

    # Descuento medio por mes
    bars2 = axes[1].bar(
        resumen['mes'], resumen['descuento_medio'],
        color= color_acento
    )
    axes[1].axhline(
        50, color= color_secundario, linestyle='--',
        linewidth=1.5, label='Umbral 50%'
    )
    for bar in bars2:
        axes[1].text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.3,
            f'{bar.get_height():.1f}%',
            ha='center', va='bottom', fontsize=12
        )
    axes[1].set_title('Descuento medio por mes (%)')
    axes[1].set_xlabel('Mes')
    axes[1].set_ylabel('Descuento medio (%)')
    axes[1].legend()

    plt.suptitle(
        'Evolución temporal — Oct/Nov/Dic 2025',
        fontsize=15, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.show()


def plot_contraste_hipotesis(df):
    """
    Gráfico específico para contrastar la hipótesis del 50%.
    Muestra qué porcentaje de subastas está por encima y por debajo.
    """
    df = df.copy()
    df['grupo'] = df['descuento_pct'].apply(
        lambda x: 'Por debajo del 50%' if x < 50 else 'Por encima del 50%'
    )

    conteo = df['grupo'].value_counts()
    pct    = df['grupo'].value_counts(normalize=True) * 100

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Barplot
    colores = [color_principal, color_secundario]
    
    

    axes[0].bar(
    conteo.index, conteo.values,
    color=colores[:len(conteo)]
    )

    for i, (p, porcentaje) in enumerate(zip(axes[0].patches, pct.values)):
        # Si la barra es muy alta, poner la etiqueta DENTRO
        altura = p.get_height()
        if altura > 200:
            # etiqueta dentro de la barra
            axes[0].annotate(
                f'{int(altura)} subastas\n({porcentaje:.1f}%)',
                (p.get_x() + p.get_width()/2, altura / 2),
                ha='center', va='center',
                fontsize=12, fontweight='bold',
                color='white'   # texto blanco para que se lea dentro
            )
        else:
            # etiqueta encima de la barra
            axes[0].annotate(
                f'{int(altura)} subastas\n({porcentaje:.1f}%)',
                (p.get_x() + p.get_width()/2, altura + 5),
                ha='center', va='bottom',
                fontsize=12, fontweight='bold',
                color='black'
            )

    axes[0].set_title('¿Por encima o debajo del 50% de descuento?')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Nº subastas')

    # Pie chart
    axes[1].pie(
        conteo.values,
        labels=conteo.index,
        colors=colores,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )
    axes[1].set_title('Proporción respecto al umbral del 50%')

    plt.suptitle('Contraste de hipótesis — Umbral 50% de descuento',
                fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()