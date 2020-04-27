# Universidade Federal do Ceará
# Departamento de Estatística e Matemática Aplicada
# Mestrado em Modelagem e Métodos Quantitativos
# Aluno: Judecir Cavalcante (judecir@gmail.com)
# Orientador: Rafael Andrade (rca.ufc@gmail.com)
import os
import pandas as pd

#os.chdir("C:/Users/User/Google Drive/UFC/MMQ/PESQUISA/MODELO DO ARRANJO LINEAR MÍNIMO PARA JOB SHOP/CODIGOS/scripts")
#os.chdir("C:/Users/User/Documents/Python Scripts/teste_mmq_jsp_minla") 
  
from pre_processamento import criar_instancias

from resolucao import teste_manne_minlafav

from pos_processamento import criar_df_comparacao


prefixo_arq="t1"
df = teste_manne_minlafav(prefixo_arq, 
                          ini_amostra=0,
                          tam_amostra=17,
                          tempo_max=3600*2, 
                          fl_primeira_sol=False
                          ,fl_heuristica_desabilitada=False)
"""
df_comp = criar_df_comparacao(df)

flags = 100*df_comp[["fl_funcao_objetivo",\
             "fl_best_bound", \
             "fl_mip_relative_gap", \
             "rel_fl_funcao_objetivo"]].sum()/df_comp["problema"].count()

print(" >>>>>>>>>> Resultados gerais: <<<<<<<<<<<<\n", flags)
df_comp.to_csv("solucoes/"+prefixo_arq+"_df_com"+".csv", index=False, sep=";", decimal=",")
"""