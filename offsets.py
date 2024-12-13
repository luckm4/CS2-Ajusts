import requests
import re
import json

# URL dos arquivos de offsets
url_arquivo1 = 'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.hpp'
url_arquivo2 = 'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.hpp'

# Função para obter o conteúdo dos arquivos
def obter_conteudo_arquivo(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Erro ao acessar o arquivo: {response.status_code}")
        return None

# Função para extrair variáveis de offset do conteúdo
def extrair_offsets(conteudo):
    offsets = {}
    # Expressão regular para capturar os offsets (exemplo de formato: m_iHealth = 0x344)
    pattern = r"([a-zA-Z_0-9]+)\s*=\s*(0x[0-9A-Fa-f]+)"
    matches = re.findall(pattern, conteudo)

    # Adiciona as variáveis encontradas ao dicionário
    for nome, valor in matches:
        offsets[nome] = int(valor, 16)  # Converte o valor hexadecimal para inteiro
    return offsets


def start():
    # Obter os dados dos dois arquivos
    conteudo_arquivo1 = obter_conteudo_arquivo(url_arquivo1)
    conteudo_arquivo2 = obter_conteudo_arquivo(url_arquivo2)

    # Extrair offsets dos arquivos
    offsets_arquivo1 = extrair_offsets(conteudo_arquivo1) if conteudo_arquivo1 else {}
    offsets_arquivo2 = extrair_offsets(conteudo_arquivo2) if conteudo_arquivo2 else {}

    # Combina os dados dos dois arquivos
    offsets_combined = {**offsets_arquivo1, **offsets_arquivo2}

    # Salvar os offsets em um arquivo JSON
    with open('offsets.json', 'w') as f:
        json.dump(offsets_combined, f)

if __name__ == "__main__":
    start()