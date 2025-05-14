# Extrator de Texto de PDF

Este projeto contém dois scripts Python para extrair texto de arquivos PDF:
1. `extrator_pdf_avancado.py` - Extrai texto com coordenadas detalhadas
2. `extrator_pdf_legivel.py` - Extrai texto de forma organizada e legível

## Requisitos

### Bibliotecas Python
```bash
pip install PyPDF2==3.0.1
pip install pytesseract==0.3.10
pip install pdf2image==1.16.3
pip install PyMuPDF==1.23.8
```

### Software Adicional
- Tesseract OCR (para PDFs escaneados)
  - Windows: Baixar e instalar do site oficial
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

## Estrutura de Pastas
O programa espera a seguinte estrutura:
```
.
├── pdf/          # Coloque seus PDFs aqui
├── txt/          # Os arquivos de texto serão salvos aqui
└── *.py          # Scripts Python
```

## Como Usar

1. Coloque seus arquivos PDF na pasta `pdf/`
2. Execute um dos scripts:
   ```bash
   python extrator_pdf_legivel.py
   # ou
   python extrator_pdf_avancado.py
   ```

## Detalhes dos Scripts

### extrator_pdf_legivel.py

Este script organiza o texto de forma mais legível:

1. **Agrupamento por Linha**:
   - Textos são agrupados pela parte inteira da coordenada Y
   - Ex: textos em Y=352.16 e Y=352.32 são considerados na mesma linha

2. **Formato de Saída**:
   ```
   === PÁGINA 1 ===
   
   Y=348 (348.32): Texto da primeira linha
   Y=352 (352.16-352.32): Primeiro_texto_Segundo_texto_Terceiro_texto
   
   === PÁGINA 2 ===
   ...
   ```

3. **Características**:
   - Mostra o Y inteiro e os valores decimais em parênteses
   - Textos na mesma linha são separados por underscore (_)
   - Páginas são claramente marcadas
   - Ordenação da esquerda para direita em cada linha

### extrator_pdf_avancado.py

Este script fornece informações detalhadas sobre cada elemento de texto:

1. **Informações Extraídas**:
   - Texto encontrado
   - Posição exata (X, Y)
   - Dimensões (largura, altura)
   - Número da página

2. **Formato de Saída**:
   ```
   RELATÓRIO DE TEXTO ENCONTRADO COM COORDENADAS
   ===========================================
   
   PÁGINA 1
   ------------------------------
   Texto: [palavra ou frase]
   Posição: x=100.00, y=50.00
   Dimensões: largura=80.00, altura=20.00
   --------------------
   ```

## Funcionalidades Principais

1. **Extração de Texto**:
   - Suporte a PDFs pesquisáveis
   - Suporte a PDFs escaneados (via OCR)
   - Preservação da ordem do texto

2. **Coordenadas**:
   - Sistema de coordenadas começa no topo esquerdo (0,0)
   - X aumenta da esquerda para direita
   - Y aumenta de cima para baixo

3. **Tratamento de Erros**:
   - Tenta primeiro extração direta
   - Se falhar, usa OCR automaticamente
   - Mensagens claras de erro

## Observações

1. **PDFs Pesquisáveis**:
   - Processamento mais rápido
   - Maior precisão na extração
   - Melhor preservação do layout

2. **PDFs Escaneados**:
   - Requer Tesseract OCR instalado
   - Processamento mais lento
   - Precisão depende da qualidade da imagem

3. **Limitações**:
   - Alguns layouts complexos podem não ser perfeitamente preservados
   - Caracteres especiais podem requerer configuração adicional do OCR
   - PDFs protegidos ou criptografados não são suportados

## Dicas de Uso

1. **Para melhor resultado**:
   - Use PDFs pesquisáveis quando possível
   - Mantenha os PDFs bem formatados
   - Evite PDFs com layouts muito complexos

2. **Ajustes possíveis**:
   - A tolerância de agrupamento pode ser ajustada no código
   - O separador de texto (_) pode ser alterado
   - O formato de saída pode ser personalizado

## Suporte

Para problemas ou sugestões, por favor:
1. Verifique se o Tesseract está instalado corretamente
2. Confirme que todas as dependências foram instaladas
3. Verifique se os PDFs não estão corrompidos ou protegidos 