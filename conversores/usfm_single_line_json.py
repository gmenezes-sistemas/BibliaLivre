import os
import re
import json

def limpar_marcadores(texto):
    texto = re.sub(r'\\add\s*|\s*\\add\*', '', texto)
    texto = re.sub(r'\\f\s\+.*?\\f\*', '', texto)
    texto = re.sub(r'\\fr\s+\d+\.\d+', '', texto)
    texto = re.sub(r'\\ft\s+[^\n]+', '', texto)
    texto = re.sub(r'\\fk\s+[^\n]+', '', texto)
    texto = re.sub(r'\\[a-z]+\*?', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def parse_usfm_para_json(arquivo_usfm):
    with open(arquivo_usfm, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    id_usfm = ''
    livro = ''
    toc1 = ''
    toc2 = ''
    toc3 = ''
    mt1 = ''
    capitulos = []

    cap_atual = None
    versiculo_atual = None
    texto_versiculo = ''

    for linha in linhas:
        linha = linha.strip()

        if linha.startswith('\\id'):
            id_usfm = linha.replace('\\id', '').strip()
        elif linha.startswith('\\toc1'):
            toc1 = linha.replace('\\toc1', '').strip()
        elif linha.startswith('\\toc2'):
            toc2 = linha.replace('\\toc2', '').strip()
            livro = toc2
        elif linha.startswith('\\toc3'):
            toc3 = linha.replace('\\toc3', '').strip()
        elif linha.startswith('\\mt1'):
            mt1 = linha.replace('\\mt1', '').strip()
        elif linha.startswith('\\c '):
            if versiculo_atual is not None and texto_versiculo:
                texto_limpo = limpar_marcadores(texto_versiculo)
                cap_atual['versiculos'].append({
                    'versiculo': versiculo_atual,
                    'texto': texto_limpo
                })
            numero_cap = int(linha.replace('\\c', '').strip())
            cap_atual = {'numero': numero_cap, 'versiculos': []}
            capitulos.append(cap_atual)
            versiculo_atual = None
            texto_versiculo = ''
        elif linha.startswith('\\v '):
            if versiculo_atual is not None and texto_versiculo:
                texto_limpo = limpar_marcadores(texto_versiculo)
                cap_atual['versiculos'].append({
                    'versiculo': versiculo_atual,
                    'texto': texto_limpo
                })
            partes = linha.split(' ', 2)
            try:
                versiculo_atual = int(partes[1])
            except:
                versiculo_atual = None
            texto_versiculo = partes[2] if len(partes) > 2 else ''
        else:
            if versiculo_atual is not None:
                texto_versiculo += ' ' + linha

    if versiculo_atual is not None and texto_versiculo:
        texto_limpo = limpar_marcadores(texto_versiculo)
        cap_atual['versiculos'].append({
            'versiculo': versiculo_atual,
            'texto': texto_limpo
        })

    return {
        #"codigoUsfm": id_usfm,
        "livro": livro,
        "informacoesLivro": {
            "tituloSumario": toc1,
            "tituloAbreviado": toc2,
            "sigla": toc3
        },
        "tituloPrincipal": mt1,
        "capitulos": capitulos
    }

def processar_pasta(pasta):
    arquivos_usfm = [f for f in os.listdir(pasta) if f.endswith('.usfm')]
    print(f'📁 Encontrados {len(arquivos_usfm)} arquivos .usfm na pasta "{pasta}".')

    for arquivo in arquivos_usfm:
        caminho_usfm = os.path.join(pasta, arquivo)
        print(f'📄 Processando: {arquivo}')
        dados_json = parse_usfm_para_json(caminho_usfm)

        nome_json = os.path.splitext(arquivo)[0] + '.json'
        caminho_json = os.path.join(pasta, nome_json)

        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)

        print(f'✅ Gerado: {nome_json}')

if __name__ == '__main__':
    pasta_alvo = '.'  # 🔧 Altere para o caminho da sua pasta com arquivos .usfm
    processar_pasta(pasta_alvo)
