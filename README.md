# Extrator de Texto de PDF

Este é um script Python que extrai texto de arquivos PDF e os salva como arquivos de texto.

## Requisitos

- Python 3.x
- PyPDF2

## Instalação

1. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

## Estrutura de Pastas

O script espera a seguinte estrutura de pastas:
- `pdf/` - Coloque seus arquivos PDF nesta pasta
- `txt/` - Os arquivos de texto extraídos serão salvos aqui

## Como usar

1. Coloque seus arquivos PDF na pasta `pdf/`
2. Execute o script:
```bash
python extrator_pdf.py
```

O script irá:
1. Processar todos os PDFs encontrados na pasta `pdf/`
2. Criar um arquivo .txt correspondente na pasta `txt/` para cada PDF
3. Mostrar o progresso do processamento no console

## Observações

- O script foi desenvolvido para extrair texto de PDFs que contêm texto pesquisável
- PDFs que são apenas imagens digitalizadas precisarão de OCR para extrair o texto
- O nome do arquivo de texto gerado será o mesmo do PDF original, mas com extensão .txt 