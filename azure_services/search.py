import os
import requests
from bs4 import BeautifulSoup
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)

# Configurações do Azure Search
service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY")
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")

def criar_indice_se_nao_existe():
    """Cria o índice de pesquisa caso não exista."""
    index_client = SearchIndexClient(
        endpoint=service_endpoint,
        credential=AzureKeyCredential(admin_key)
    )

    if index_name not in [index for index in index_client.list_index_names()]:
        campos = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="titulo", type=SearchFieldDataType.String),
            SearchableField(name="conteudo", type=SearchFieldDataType.String),
            SimpleField(name="url", type=SearchFieldDataType.String)
        ]

        indice = SearchIndex(name=index_name, fields=campos)
        index_client.create_or_update_index(indice)
        print(f"Índice '{index_name}' criado com sucesso.")
    else:
        print(f"Índice '{index_name}' já existe.")


def extrair_conteudo_url(url):
    """Extrai o conteúdo HTML de uma URL da documentação STRIDE."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        titulo = soup.title.string if soup.title else "Sem título"

        # Nova lógica para extração do conteúdo principal
        conteudo_documentacoes_divs = soup.find_all('div', class_='content')
        print(conteudo_documentacoes_divs)

        if conteudo_documentacoes_divs:
            conteudo = ""
            for div in conteudo_documentacoes_divs:
                paragrafos = div.find_all('p')
                # Concatena o texto de todos os parágrafos encontrados em cada div
                conteudo += ' ' + ' '.join(p.get_text(strip=True) for p in paragrafos)
            conteudo = conteudo.strip()
        else:
            # Fallback
            conteudo_principal = soup.find('main') or soup.find('article') or soup.find('div', id='main')
            if conteudo_principal:
                # Remover scripts e estilos
                for script in conteudo_principal(["script", "style"]):
                    script.extract()
                conteudo = conteudo_principal.get_text(separator=' ', strip=True)
            else:
                conteudo = soup.body.get_text(separator=' ', strip=True) if soup.body else ""

        return {
            "titulo": titulo,
            "conteudo": conteudo,
            "url": url
        }
    except Exception as e:
        print(f"Erro ao processar URL {url}: {str(e)}")
        return None


def carregar_urls():
    """Carrega URLs do arquivo de texto."""
    try:
        # Obtém o caminho absoluto do script atual
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Constrói o caminho para o arquivo de URLs
        # Ajuste o número de ".." conforme a estrutura de diretórios do seu projeto
        url_file_path = os.path.join(script_dir, "..", "documentacao_stride", "urls_documentacao_stride.txt")

        print(f"Tentando abrir o arquivo em: {url_file_path}")

        with open(url_file_path, "r") as arquivo:
            return [linha.strip() for linha in arquivo if linha.strip()]
    except Exception as e:
        print(f"Erro ao ler arquivo de URLs: {str(e)}")
        return []

def indexar_documentacao():
    """Função principal para indexar a documentação STRIDE."""
    criar_indice_se_nao_existe()

    search_client = SearchClient(
        endpoint=service_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(admin_key)
    )

    urls = carregar_urls()
    print(f"Processando {len(urls)} URLs...")

    documentos = []
    for i, url in enumerate(urls):
        documento = extrair_conteudo_url(url)
        if documento:
            documento["id"] = f"stride-doc-{i+1}"
            documentos.append(documento)

    if documentos:
        result = search_client.upload_documents(documents=documentos)
        print(f"Indexados {len(documentos)} documentos com sucesso.")
    else:
        print("Nenhum documento para indexar.")

if __name__ == "__main__":
    indexar_documentacao()