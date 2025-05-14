import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
from pathlib import Path
import fitz  # PyMuPDF - melhor para extrair coordenadas

def extrair_texto_com_ocr(caminho_arquivo):
    """Extrai texto de PDFs escaneados usando OCR com coordenadas."""
    try:
        # Converte PDF para imagens
        paginas = convert_from_path(caminho_arquivo)
        resultado_completo = []
        
        # Processa cada página
        for num_pagina, pagina in enumerate(paginas, 1):
            # Usa OCR para extrair texto da imagem com coordenadas
            dados = pytesseract.image_to_data(pagina, lang='por', output_type=pytesseract.Output.DICT)
            
            # Organiza os resultados
            for i in range(len(dados['text'])):
                if dados['text'][i].strip():  # Se houver texto
                    resultado_completo.append({
                        'pagina': num_pagina,
                        'texto': dados['text'][i],
                        'x': dados['left'][i],
                        'y': dados['top'][i],
                        'largura': dados['width'][i],
                        'altura': dados['height'][i]
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
            # Extrai blocos de texto com suas coordenadas
            blocos = pagina.get_text("dict")["blocks"]
            
            for bloco in blocos:
                if "lines" in bloco:
                    for linha in bloco["lines"]:
                        for span in linha["spans"]:
                            bbox = span["bbox"]  # (x0, y0, x1, y1)
                            resultado_completo.append({
                                'pagina': num_pagina + 1,
                                'texto': span["text"],
                                'x': bbox[0],
                                'y': bbox[1],
                                'largura': bbox[2] - bbox[0],
                                'altura': bbox[3] - bbox[1]
                            })
        
        doc.close()
        return resultado_completo
    except Exception as e:
        print(f"Erro na extração normal: {str(e)}")
        return None

def processar_pdf(caminho_arquivo):
    """Tenta extrair texto primeiro normalmente, se falhar usa OCR."""
    # Tenta extração normal primeiro
    resultado = extrair_texto_normal(caminho_arquivo)
    
    # Se não conseguiu extrair texto ou o resultado está vazio, tenta OCR
    if not resultado:
        print("Texto não encontrado, tentando OCR...")
        resultado = extrair_texto_com_ocr(caminho_arquivo)
    
    return resultado

def salvar_resultado(resultado, caminho_txt):
    """Salva o resultado em formato texto com coordenadas."""
    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO DE TEXTO ENCONTRADO COM COORDENADAS\n")
        arquivo.write("=" * 50 + "\n\n")
        
        pagina_atual = None
        for item in resultado:
            # Se mudou de página, adiciona cabeçalho
            if pagina_atual != item['pagina']:
                pagina_atual = item['pagina']
                arquivo.write(f"\nPÁGINA {pagina_atual}\n")
                arquivo.write("-" * 30 + "\n")
            
            # Escreve o texto e suas coordenadas
            arquivo.write(f"Texto: {item['texto']}\n")
            arquivo.write(f"Posição: x={item['x']:.2f}, y={item['y']:.2f}\n")
            arquivo.write(f"Dimensões: largura={item['largura']:.2f}, altura={item['altura']:.2f}\n")
            arquivo.write("-" * 20 + "\n")

def processar_pdfs():
    # Cria os diretórios se não existirem
    Path("pdf").mkdir(exist_ok=True)
    Path("txt").mkdir(exist_ok=True)
    
    # Lista todos os arquivos PDF
    arquivos_pdf = [f for f in os.listdir("pdf") if f.lower().endswith('.pdf')]
    
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta 'pdf'!")
        return
    
    print(f"Encontrados {len(arquivos_pdf)} arquivos PDF para processar.")
    
    for arquivo_pdf in arquivos_pdf:
        caminho_pdf = os.path.join("pdf", arquivo_pdf)
        nome_arquivo = os.path.splitext(arquivo_pdf)[0]
        caminho_txt = os.path.join("txt", f"{nome_arquivo}_com_coordenadas.txt")
        
        print(f"\nProcessando: {arquivo_pdf}")
        
        resultado = processar_pdf(caminho_pdf)
        
        if resultado:
            salvar_resultado(resultado, caminho_txt)
            print(f"✓ Texto e coordenadas salvos em: {caminho_txt}")
        else:
            print(f"❌ Não foi possível extrair texto de: {arquivo_pdf}")

if __name__ == "__main__":
    processar_pdfs() 