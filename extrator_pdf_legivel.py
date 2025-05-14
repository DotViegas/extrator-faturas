import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
from pathlib import Path
import fitz
from operator import itemgetter
from collections import defaultdict
import math

def extrair_texto_com_ocr(caminho_arquivo):
    """Extrai texto de PDFs escaneados usando OCR com coordenadas."""
    try:
        paginas = convert_from_path(caminho_arquivo)
        resultado_completo = []
        
        for num_pagina, pagina in enumerate(paginas, 1):
            dados = pytesseract.image_to_data(pagina, lang='por', output_type=pytesseract.Output.DICT)
            
            for i in range(len(dados['text'])):
                if dados['text'][i].strip():
                    resultado_completo.append({
                        'pagina': num_pagina,
                        'texto': dados['text'][i].strip(),
                        'x': dados['left'][i],
                        'y': dados['top'][i]
                    })
            
        return resultado_completo
    except Exception as e:
        print(f"Erro no OCR: {str(e)}")
        return None

def extrair_texto_normal(caminho_arquivo):
    """Extrai texto de PDFs pesquisáveis com coordenadas usando PyMuPDF."""
    try:
        resultado_completo = []
        doc = fitz.open(caminho_arquivo)
        
        for num_pagina in range(len(doc)):
            pagina = doc[num_pagina]
            blocos = pagina.get_text("dict")["blocks"]
            
            for bloco in blocos:
                if "lines" in bloco:
                    for linha in bloco["lines"]:
                        for span in linha["spans"]:
                            if span["text"].strip():
                                resultado_completo.append({
                                    'pagina': num_pagina + 1,
                                    'texto': span["text"].strip(),
                                    'x': span["bbox"][0],
                                    'y': span["bbox"][1]
                                })
        
        doc.close()
        return resultado_completo
    except Exception as e:
        print(f"Erro na extração normal: {str(e)}")
        return None

def processar_pdf(caminho_arquivo):
    """Tenta extrair texto primeiro normalmente, se falhar usa OCR."""
    resultado = extrair_texto_normal(caminho_arquivo)
    
    if not resultado:
        print("Texto não encontrado, tentando OCR...")
        resultado = extrair_texto_com_ocr(caminho_arquivo)
    
    return resultado

def organizar_texto_por_linha(resultado):
    """Organiza o texto agrupando por página e linha (coordenada Y)."""
    if not resultado:
        return []

    # Agrupa por página
    paginas = defaultdict(list)
    for item in resultado:
        paginas[item['pagina']].append(item)
    
    texto_organizado = []
    
    # Para cada página
    for num_pagina in sorted(paginas.keys()):
        itens_pagina = paginas[num_pagina]
        
        # Agrupa itens por coordenada Y (usando apenas a parte inteira)
        linhas = defaultdict(list)
        
        for item in itens_pagina:
            # Usa apenas a parte inteira do Y como chave
            y_key = math.floor(item['y'])
            linhas[y_key].append(item)
        
        # Para cada linha (mesmo Y inteiro)
        for y in sorted(linhas.keys()):
            # Ordena os itens da linha por X (da esquerda para direita)
            itens_linha = sorted(linhas[y], key=lambda x: x['x'])
            
            # Pega o menor e maior Y decimal do grupo para mostrar o intervalo
            y_decimais = [item['y'] for item in itens_linha]
            y_min = min(y_decimais)
            y_max = max(y_decimais)
            
            # Se houver variação nos decimais, mostra o intervalo
            if y_min != y_max:
                y_info = f"Y={y} ({y_min:.2f}-{y_max:.2f}): "
            else:
                y_info = f"Y={y} ({y_min:.2f}): "
            
            # Junta os textos com underscore
            linha_texto = y_info + "_".join(item['texto'] for item in itens_linha)
            texto_organizado.append(linha_texto)
        
        # Adiciona uma linha em branco e marcador de página
        texto_organizado.append("")
        texto_organizado.append(f"=== PÁGINA {num_pagina} ===")
        texto_organizado.append("")
    
    return texto_organizado

def salvar_resultado_legivel(texto_organizado, caminho_txt):
    """Salva o resultado em formato texto legível."""
    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        for linha in texto_organizado:
            arquivo.write(linha + "\n")

def processar_pdfs():
    Path("pdf").mkdir(exist_ok=True)
    Path("txt").mkdir(exist_ok=True)
    
    arquivos_pdf = [f for f in os.listdir("pdf") if f.lower().endswith('.pdf')]
    
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta 'pdf'!")
        return
    
    print(f"Encontrados {len(arquivos_pdf)} arquivos PDF para processar.")
    
    for arquivo_pdf in arquivos_pdf:
        caminho_pdf = os.path.join("pdf", arquivo_pdf)
        nome_arquivo = os.path.splitext(arquivo_pdf)[0]
        caminho_txt = os.path.join("txt", f"{nome_arquivo}_legivel.txt")
        
        print(f"\nProcessando: {arquivo_pdf}")
        
        resultado = processar_pdf(caminho_pdf)
        
        if resultado:
            texto_organizado = organizar_texto_por_linha(resultado)
            salvar_resultado_legivel(texto_organizado, caminho_txt)
            print(f"✓ Texto organizado salvo em: {caminho_txt}")
        else:
            print(f"❌ Não foi possível extrair texto de: {arquivo_pdf}")

if __name__ == "__main__":
    processar_pdfs() 