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

def encontrar_texto_proximo(itens, x_alvo, y_alvo, tolerancia=2, coordenadas_alternativas=None):
    """Encontra o texto mais próximo das coordenadas alvo com tolerância de 2 pixels."""
    # Tenta encontrar nas coordenadas principais
    for item in itens:
        if (abs(item['x'] - x_alvo) <= tolerancia and 
            abs(item['y'] - y_alvo) <= tolerancia):
            return item['texto'], (x_alvo, y_alvo)
    
    # Se não encontrou e existem coordenadas alternativas, tenta nelas
    if coordenadas_alternativas:
        for x_alt, y_alt in coordenadas_alternativas:
            for item in itens:
                if (abs(item['x'] - x_alt) <= tolerancia and 
                    abs(item['y'] - y_alt) <= tolerancia):
                    return item['texto'], (x_alt, y_alt)
    
    return "Não encontrado", None

def extrair_dados_especificos(resultado):
    """Extrai dados específicos com base nas coordenadas fornecidas."""
    if not resultado:
        return []
    
    # Agrupa todos os itens da primeira página
    itens_pagina1 = [item for item in resultado if item['pagina'] == 1]
    
    # Coordenadas específicas para buscar (principal e alternativas)
    coordenadas_busca = {
        'DATA DE LEITURA': {
            'principal': (368.40, 299.58),
            'alternativas': [(406.20, 160.47)]
        },
        'DATA DE EMISSÃO': {
            'principal': (410.40, 199.76),
            'alternativas': []
        },
        'VALOR DA FATURA (R$)': {
            'principal': (235.80, 249.21),
            'alternativas': []
        },
        'LEITURA ANTERIOR': {
            'principal': (292.80, 299.58),
            'alternativas': [(359.16, 160.47)]
        },
        'PERÍODO DE LEITURA': {
            'principal': (458.91, 160.47),
            'alternativas': []
        }
    }
    
    # Encontra os dados específicos
    dados_encontrados = []
    dados_encontrados.append("=== DADOS PEGOS ===")
    
    for rotulo, coords in coordenadas_busca.items():
        texto, coords_encontradas = encontrar_texto_proximo(
            itens_pagina1, 
            coords['principal'][0], 
            coords['principal'][1],
            coordenadas_alternativas=coords['alternativas']
        )
        
        if texto != "Não encontrado" and coords_encontradas:
            x, y = coords_encontradas
            dados_encontrados.append(f"{rotulo}: {texto} (encontrado em x={x}±2, y={y}±2)")
        else:
            dados_encontrados.append(f"{rotulo}: {texto}")
    
    # Extrai itens da fatura (região específica)
    dados_encontrados.append("\nITENS DA FATURA:")
    
    # Dicionário para armazenar os itens da fatura por Y
    itens_por_y = defaultdict(list)
    
    # Coleta todos os itens na região específica (x: 26-425, y: 347-534)
    for item in itens_pagina1:
        if (26 <= item['x'] <= 425 and
            347 <= item['y'] <= 534):
            y_key = math.floor(item['y'])
            itens_por_y[y_key].append(item)
    
    # Palavras-chave para identificar itens da fatura
    palavras_chave = [
        "KWH", "CONSUMO", "DEMANDA", "POTÊNCIA", "CONT", "MUNICIPAL",
        "ENERGIA", "CONTRIB", "ICMS", "PIS", "COFINS"
    ]
    
    # Flag para indicar se já encontramos LANÇAMENTOS E SERVIÇOS
    apos_lancamentos = False
    
    # Para cada linha Y, processa os itens
    for y in sorted(itens_por_y.keys()):
        # Ordena itens por X
        itens = sorted(itens_por_y[y], key=lambda x: x['x'])
        textos = [item['texto'] for item in itens]
        
        if not textos:  # Se não há textos, pula
            continue
        
        primeiro_texto = textos[0].upper()
        
        # Verifica se encontrou a seção de LANÇAMENTOS E SERVIÇOS
        if "LANÇAMENTOS E SERVIÇOS" in primeiro_texto:
            apos_lancamentos = True
            continue
            
        # Se encontrou uma linha com alguma das palavras-chave
        if any(palavra in primeiro_texto for palavra in palavras_chave):
            descricao = textos[0]  # Primeiro item é a descrição
            valores = [v for v in textos[1:] if v]  # Remove valores vazios
            
            if not valores:  # Se não há valores, pula
                continue
                
            dados_encontrados.append(f"\nItem: {descricao}")
            
            if apos_lancamentos:
                # Após LANÇAMENTOS E SERVIÇOS, usa formato simplificado
                if valores:  # Se houver algum valor
                    dados_encontrados.append(f"Valor (R$): {valores[0]}")
            else:
                # Antes de LANÇAMENTOS E SERVIÇOS, usa formato detalhado
                if len(valores) >= 8:
                    unidade = valores[0] if valores[0] in ["KW", "KWH", "UN"] else "UN"
                    dados_encontrados.append(f"Unidade: {unidade}")
                    dados_encontrados.append(f"Quantidade: {valores[1]}")
                    dados_encontrados.append(f"Preço unitário (R$) com tributos: {valores[2]}")
                    dados_encontrados.append(f"Valor (R$): {valores[3]}")
                    dados_encontrados.append(f"PIS/COFINS (R$): {valores[4]}")
                    dados_encontrados.append(f"Base Cálculo ICMS (R$): {valores[5]}")
                    dados_encontrados.append(f"Alíquota ICMS (%): {valores[6]}")
                    dados_encontrados.append(f"ICMS (R$): {valores[7]}")
                    if len(valores) > 8:
                        dados_encontrados.append(f"Tarifa Unitária: {valores[8]}")
                else:
                    # Se não tiver todos os valores, ainda tenta formatar o que tem
                    campos = ["Unidade", "Quantidade", "Preço unitário (R$) com tributos", 
                             "Valor (R$)", "PIS/COFINS (R$)", "Base Cálculo ICMS (R$)", 
                             "Alíquota ICMS (%)", "ICMS (R$)", "Tarifa Unitária"]
                    for i, valor in enumerate(valores):
                        if i < len(campos):
                            dados_encontrados.append(f"{campos[i]}: {valor}")
    
    dados_encontrados.append("")  # Linha em branco no final
    return dados_encontrados

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
    
    # Primeiro adiciona os dados específicos
    texto_organizado.extend(extrair_dados_especificos(resultado))
    texto_organizado.append("")  # Linha em branco
    
    # Para cada página
    for num_pagina in sorted(paginas.keys()):
        itens_pagina = paginas[num_pagina]
        
        texto_organizado.append(f"=== PÁGINA {num_pagina} ===")
        texto_organizado.append("")
        
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
        
        # Adiciona uma linha em branco entre páginas
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