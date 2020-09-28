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

def ler_tabelas_teste(lista_nome_arquivo):
    df = pd.DataFrame()
    for arquivo in lista_nome_arquivo:
        # Formatando arquivo se estiver com erro na escrita (atualmente meu 
        # codigo esta com esse bug)
        s = open(arquivo).read()
        s = s.replace('; ', ';')
        s = s.replace('; ', ';')
        f = open(arquivo, 'w')
        f.write(s)
        f.close()
        # Unindo dataframes
        df = df.append(pd.read_csv(arquivo, sep=";", index_col=False, decimal="."))
    return df

def criar_tabela_layout_artigo(lista_nome_arquivo = ['solucoes/sbpo/t1_results.csv', 'solucoes/sbpo/t2_results.csv']):
    # Definindo nome das colunas
    colunas_instancias = ["problema", "num_jobs", "num_maquina"]
    colunas_rl = ["funcao_objetivo", "time"]
    colunas_int = ["funcao_objetivo", "time", "mip_relative_gap"]

    # Lendo tabelas dos arquivos
    df = ler_tabelas_teste(lista_nome_arquivo)
    
    
    # Renomeando o nome do modelo
    df["modelo"] = df["modelo"].replace("minla_fav", "manne_desig")
    
    # Definindo listas
    modelos = df["modelo"].unique()
    fl_inteiro = df["fl_inteiro"].unique()
    
    lista_df = []
    df_retorno = pd.DataFrame(columns = colunas_instancias)
    for m in modelos:
        df_modelo = pd.DataFrame(columns = colunas_instancias)
        for fl in fl_inteiro:
            filtro = (df["fl_inteiro"] == fl) & \
                     (df["modelo"]==m)
            df_aux = df[filtro]
            if fl:
                df_aux = df_aux[colunas_instancias+colunas_int]
                df_aux.columns = colunas_instancias + [m + " - " +c for c in colunas_int]
            else:
                df_aux = df_aux[colunas_instancias+colunas_rl]
                df_aux.columns = colunas_instancias + [m + " - " +c + "(RL)" for c in colunas_rl]
            df_modelo = pd.merge(df_modelo, df_aux, how="outer", on=colunas_instancias)
        lista_df.append({"modelo":m, "df":df_modelo})
        df_retorno = pd.merge(df_retorno, df_modelo, how="outer", on=colunas_instancias)
    
    return lista_df, df_retorno