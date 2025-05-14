import os
from pathlib import Path
from difflib import SequenceMatcher

def ler_arquivo(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho}: {str(e)}")
        return None

def comparar_arquivos_trabalho(diretorio):
    print(f"\n{'='*50}")
    print(f"Analisando trabalho: {os.path.basename(diretorio)}")
    print(f"{'='*50}")
    
    # Obter todos os arquivos .txt no diretório
    arquivos = list(Path(diretorio).glob('*.txt'))
    
    if len(arquivos) < 2:
        print(f"Não há arquivos suficientes para comparar neste trabalho.")
        return
    
    print(f"\nTotal de arquivos encontrados: {len(arquivos)}")
    
    # Comparar cada arquivo com os outros
    arquivos_identicos = []
    arquivos_diferentes = []
    
    for i in range(len(arquivos)):
        for j in range(i + 1, len(arquivos)):
            arquivo1 = arquivos[i]
            arquivo2 = arquivos[j]
            
            conteudo1 = ler_arquivo(arquivo1)
            conteudo2 = ler_arquivo(arquivo2)
            
            if conteudo1 is None or conteudo2 is None:
                continue
            
            # Comparar os conteúdos
            if conteudo1 == conteudo2:
                arquivos_identicos.append((arquivo1.name, arquivo2.name))
            else:
                similaridade = SequenceMatcher(None, conteudo1, conteudo2).ratio() * 100
                arquivos_diferentes.append((arquivo1.name, arquivo2.name, similaridade))
    
    # Exibir resultados
    if arquivos_identicos:
        print("\nArquivos IDÊNTICOS encontrados:")
        for arq1, arq2 in arquivos_identicos:
            print(f"- {arq1} = {arq2}")
    
    if arquivos_diferentes:
        print("\nArquivos DIFERENTES encontrados:")
        for arq1, arq2, similaridade in arquivos_diferentes:
            print(f"- {arq1} vs {arq2} (Similaridade: {similaridade:.2f}%)")
    
    print("\nAnálise concluída para este trabalho.")

def processar_trabalhos(diretorio_base):
    if not os.path.exists(diretorio_base):
        print(f"O diretório {diretorio_base} não existe!")
        return
    
    # Listar todos os subdiretórios (trabalhos)
    trabalhos = [d for d in os.listdir(diretorio_base) 
                if os.path.isdir(os.path.join(diretorio_base, d))]
    
    if not trabalhos:
        print("Nenhum trabalho (pasta) encontrado para análise!")
        return
    
    print(f"Encontrados {len(trabalhos)} trabalhos para análise.")
    
    # Processar cada trabalho
    for trabalho in trabalhos:
        caminho_trabalho = os.path.join(diretorio_base, trabalho)
        comparar_arquivos_trabalho(caminho_trabalho)

if __name__ == "__main__":
    print("Iniciando análise de trabalhos...")
    processar_trabalhos("comparar") 