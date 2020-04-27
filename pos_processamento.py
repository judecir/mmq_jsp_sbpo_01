import json
import pandas as pd
import os
import xml.etree.ElementTree as ET

def criar_pasta_se_n_existe(nome_pasta):
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
        
def nome_arquivo_geral(nome_modelo, m, n, prefixo=""):    
    #return prefixo+"_"+nome_modelo+"_"+"{:002}".format(n)+"jobs_"+"{:002}".format(m)+"maq"
    return prefixo

def nome_arquivo_lp(nome_modelo, m, n, prefixo=""):
    criar_pasta_se_n_existe("lps")
    return "lps/"+nome_arquivo_geral(nome_modelo, m, n, prefixo)+".lp"

def nome_arquivo_log(nome_modelo, m, n, prefixo=""):   
    criar_pasta_se_n_existe("logs") 
    return "logs/"+nome_arquivo_geral(nome_modelo, m, n, prefixo)+".txt"

def nome_arquivo_sol(nome_modelo, m, n, prefixo=""):    
    criar_pasta_se_n_existe("valor_variaveis")
    return "valor_variaveis/"+nome_arquivo_geral(nome_modelo, m, n, prefixo)+".json"

def exportar_solucao(solucao, nome_modelo, m, n, prefixo=""):
    with open(nome_arquivo_sol(nome_modelo, m, n, prefixo=prefixo), 'w') as lout:
        solucao.export(lout)
        
def ler_solucao(nome_modelo, m, n):
    nome_arquivo = nome_arquivo_sol(nome_modelo, m, n)
    with open(nome_arquivo) as json_file:
        data = json.load(json_file)
        solution = data["CPLEXSolution"]
        df_variable = pd.DataFrame(solution["variables"])
        print(df_variable.head())
        
        df_lincon= pd.DataFrame(solution["linearConstraints"])
        print(df_lincon.head())
        
        return df_variable, df_lincon
    
def criar_df_comparacao(resultado, colunas_comparar = ["problema","funcao_objetivo", "mip_relative_gap", "best_bound", "nb_iterations", "time"], coluna_pivot = ["problema"]):
    problemas = resultado["problema"].unique()
    modelos = resultado["modelo"].unique()
    df = pd.DataFrame()
    for p in problemas:
        df_modelo = pd.DataFrame()
        for m in modelos:
            filtro_int = (resultado["fl_inteiro"]==True) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]==m)
            df_filtro_int = resultado[filtro_int]
            df_filtro_int.columns = coluna_pivot + [m+" "+c for c in df_filtro_int.columns[1:]]

            filtro_real = (resultado["fl_inteiro"]==False) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]==m)
            df_filtro_real = resultado[filtro_real]
            df_filtro_real = df_filtro_real.drop(["best_bound", "mip_relative_gap"], axis=1)
            df_filtro_real.columns = coluna_pivot + [m+" "+c for c in df_filtro_real.columns[1:]]

        df
            
        filtro_mn_int = (resultado["fl_inteiro"]==True) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]=="manne")
        filtro_ml_int = (resultado["fl_inteiro"]==True) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]=="minla_fav")
        
        df_mn_int = resultado.loc[filtro_mn_int, colunas_comparar].copy()
        df_mn_int.columns = coluna_pivot + ["Manne "+c for c in df_mn_int.columns[1:]]
        
        df_ml_int = resultado.loc[filtro_ml_int, colunas_comparar].copy()
        df_ml_int.columns = coluna_pivot + ["MinLA "+c for c in df_ml_int.columns[1:]]
        
        df_mn_ml_int = pd.merge(df_mn_int, df_ml_int, how="outer", on=coluna_pivot)

        filtro_mn_real = (resultado["fl_inteiro"]==False) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]=="manne")
        filtro_ml_real = (resultado["fl_inteiro"]==False) & (resultado[coluna_pivot[0]]==p) & (resultado["modelo"]=="minla_fav")
        
        df_mn_real = resultado.loc[filtro_mn_real, colunas_comparar].copy()
        df_mn_real = df_mn_real.drop(["best_bound", "mip_relative_gap"], axis=1)
        df_mn_real.columns = coluna_pivot + ["Manne Rel. "+c for c in df_mn_real.columns[1:]]
        
        df_ml_real = resultado.loc[filtro_ml_real, colunas_comparar].copy()
        df_ml_real = df_ml_real.drop(["best_bound", "mip_relative_gap"], axis=1)
        df_ml_real.columns = coluna_pivot + ["MinLA Rel. "+c for c in df_ml_real.columns[1:]]
        
        df_mn_ml_real = pd.merge(df_mn_real, df_ml_real, how="outer", on=coluna_pivot)
        
        df_mn_ml = pd.merge(df_mn_ml_int, df_mn_ml_real, how="outer", on=coluna_pivot)
        
        df = df.append(df_mn_ml)
        
    colunas_comparar_int = ["funcao_objetivo", "best_bound", "mip_relative_gap", "time"]
    colunas_comparar_real = ["funcao_objetivo", "time"]
    
    for c in colunas_comparar_int:
        nome_flag = "fl_"+c
        nome_dif = "dif_"+c
        df[nome_flag] = df["MinLA "+c] > df["Manne "+c]
        df[nome_dif] = df["MinLA "+c] - df["Manne "+c]
    for c in colunas_comparar_real:
        nome_flag = "rel_fl_"+c
        nome_dif = "rel_dif_"+c
        df[nome_flag] = df["MinLA Rel. "+c] > df["Manne Rel. "+c]
        df[nome_dif] = df["MinLA Rel. "+c] - df["Manne Rel. "+c]
        
    
    return df

def estruturar_solucoes_intermed(nome_pasta):
    nomes_arquivos = os.listdir(os.getcwd()+"/"+nome_pasta)
    solucoes = [{"funcao_objetivo":child.get('objectiveValue')}
                for arq in nomes_arquivos if 'sol-' in arq
                for child in ET.parse(nome_pasta+"/"+arq).getroot().findall("header") 
             ]                
    return solucoes
