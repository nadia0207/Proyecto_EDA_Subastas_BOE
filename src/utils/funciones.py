"""
funciones.py
Funciones auxiliares para el EDA de Subastas BOE
"""

import pandas as pd
import numpy as np
import re

# -------------LIMPIEZA -------------------------------
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

# --------------------- ANÁLISIS--------------------------
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