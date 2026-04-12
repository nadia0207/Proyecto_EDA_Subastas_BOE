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
    - Convierte lotes a int
    - Calcula descuento_pct y duracion_dias
    Devuelve el DataFrame limpio.
    """
    df = df.copy()

    # Eliminar columnas duplicadas e innecesarias
    cols_eliminar = [
        'id_sub', 'referencia_det', 'num_lotes_listado',  # duplicadas
        'url_detalle', 'anuncio_boe',                      # no aportan
        'fecha_conclusion_listado',                        # formato sucio
        'forma_adjudicacion', 'expediente', 'cuenta_expediente',  # muchos nulos
    ]
    # Solo eliminar las que existan en el df
    cols_eliminar = [c for c in cols_eliminar if c in df.columns]
    df = df.drop(columns=cols_eliminar)

    # Convertir fechas
    for col in ['fecha_inicio', 'fecha_conclusion']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Lotes a int
    if 'lotes' in df.columns:
        df['lotes'] = df['lotes'].fillna(1).astype(int)

    # Calcular descuento_pct
    mask = (
        df['tasacion_eur'].notna() &
        df['valor_subasta_eur'].notna() &
        (df['tasacion_eur'] > 0)
    )
    df.loc[mask, 'descuento_pct'] = (
        (df.loc[mask, 'tasacion_eur'] - df.loc[mask, 'valor_subasta_eur'])
        / df.loc[mask, 'tasacion_eur'] * 100
    ).round(2)

    # Calcular duración en días
    mask_fechas = df['fecha_inicio'].notna() & df['fecha_conclusion'].notna()
    df.loc[mask_fechas, 'duracion_dias'] = (
        df.loc[mask_fechas, 'fecha_conclusion'] -
        df.loc[mask_fechas, 'fecha_inicio']
    ).dt.days

    return df.reset_index(drop=True)

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
    """Imprime un resumen rápido del dataset."""
    print('=' * 45)
    print('  RESUMEN DEL DATASET')
    print('=' * 45)
    print(f'  Filas          : {df.shape[0]:,}')
    print(f'  Columnas       : {df.shape[1]}')
    print(f'\n  Tipos de subasta:')
    print(df['tipo_subasta'].value_counts().to_string())
    if 'descuento_pct' in df.columns:
        print(f'\n  Descuento sobre tasación (%):')
        print(df['descuento_pct'].describe().round(2).to_string())
    print('=' * 45)