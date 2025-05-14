import PyPDF2
import os
from pathlib import Path

def extrair_texto_pdf(caminho_arquivo):
    # Abre o arquivo PDF em modo binário
    with open(caminho_arquivo, 'rb') as arquivo:
        # Cria um objeto leitor de PDF
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        
        # Obtém o número total de páginas
        num_paginas = len(leitor_pdf.pages)
        
        # String para armazenar todo o texto
        texto_completo = ""
        
        # Itera sobre todas as páginas
        for pagina in range(num_paginas):
            # Obtém a página atual
            pagina_atual = leitor_pdf.pages[pagina]
            
            # Extrai o texto da página
            texto_completo += pagina_atual.extract_text()
            texto_completo += "\n\n"  # Adiciona espaço entre páginas
            
        return texto_completo

def processar_pdfs():
    # Cria os diretórios se não existirem
    Path("pdf").mkdir(exist_ok=True)
    Path("txt").mkdir(exist_ok=True)
    
    # Lista todos os arquivos PDF na pasta pdf
    arquivos_pdf = [f for f in os.listdir("pdf") if f.lower().endswith('.pdf')]
    
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta 'pdf'!")
        return
    
    print(f"Encontrados {len(arquivos_pdf)} arquivos PDF para processar.")
    
    for arquivo_pdf in arquivos_pdf:
        caminho_pdf = os.path.join("pdf", arquivo_pdf)
        nome_arquivo = os.path.splitext(arquivo_pdf)[0]
        caminho_txt = os.path.join("txt", f"{nome_arquivo}.txt")
        
        print(f"\nProcessando: {arquivo_pdf}")
        try:
            # Extrai o texto do PDF
            texto = extrair_texto_pdf(caminho_pdf)
            
            # Salva o texto em um arquivo na pasta txt
            with open(caminho_txt, "w", encoding="utf-8") as arquivo_texto:
                arquivo_texto.write(texto)
            print(f"✓ Texto salvo em: {caminho_txt}")
            
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo_pdf}: {str(e)}")

if __name__ == "__main__":
    processar_pdfs() 