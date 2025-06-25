import streamlit as st
import json

from azure_services import search
from openai_services import ai_flow


# Show title and description.
st.title("📄 Análise de Vulnerabilidade em Arquitetura de Software")
st.write(
    "Faça o upload da sua arquitetura de software em jpeg, png ou pdf e receba o relatório de vulnerabilidades que ela possa ter."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = ""


# Campo para a chave, salva na sessão
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

# Campo de entrada para a chave
if not st.session_state["openai_api_key"]:
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("Insira sua OpenAI API key para continuar", icon="🗝️")
    st.info("Importante que a sua chave tenha acesso ao modelo `o4-mini-2025-04-16`", icon="ℹ️")

    # Atualiza a sessão quando o usuário digita
    if api_key:
        st.session_state["openai_api_key"] = api_key
        st.rerun()
else:
    # Cria o cliente
    chat = ai_flow.Chat(st.session_state["openai_api_key"], model="o4-mini-2025-04-16")

    # Upload da arquitetura
    arquitetura = st.file_uploader(
        "Faça o upload da sua arquitetura (.pdf/.jpeg/.png)", type=("pdf", "jpeg", "png")
    )
    if arquitetura:

        
        with st.spinner('Analisando arquitetura... Por favor, aguarde.'):
            response = chat.read_architecture(arquitetura)  
            try:
                resultado = json.loads(response)
            except json.JSONDecodeError as e:
                st.error("Erro ao converter resposta para JSON.")
                st.text(response)  # Mostra o conteúdo bruto para depurar
                raise e
        
        st.subheader("📦 Componentes Identificados")
        st.write(resultado.get("componentes_identificados", []))

        st.subheader("🧠 Descrição dos Componentes")
        for componente, descricao in resultado.get("descricao_componentes", {}).items():
            st.markdown(f"**{componente}**: {descricao}")

        st.subheader("🔁 Fluxo da Aplicação")
        st.write(resultado.get("fluxo_aplicacao", "Fluxo não identificado."))
                    
        # TODO: Alterar o prompt para que o retorno seja no formato que a lib de análise da OWASP precisa pra rodar.
        # TODO: Alterar o retorno para trazer o relatório de vulnerabilidades usando a metodologia STRIDE como base.
        # TODO: Incluir botão para download do relatório gerado em pdf.
        
        st.success("Análise concluída com sucesso!", icon="✅")

        with st.spinner('Analisando itens de risco baseado na metodologia OWASP... Por favor, aguarde.'):

            search_rag = search.Search()
        
            response = search_rag.search_topic("Threat")

            st.subheader("Resultados da busca:")
            for item in response:
                with st.expander(f"📄 {item['titulo']}"):
                    st.write(f"**ID:** {item['id']}")
                    st.write(f"**Conteúdo:** {item['conteudo']}")
                    st.markdown(f"[🔗 Acessar documento]({item['url']})", unsafe_allow_html=True)

            docs_para_analise = []
            docs_para_analise.append({
                "id": item["id"],
                "conteudo": item["conteudo"]
            })
            

            resultado_items = chat.check_vulnerability_per_item("items", docs_para_analise)
            with st.expander(f"🔍 Resultado da Análise item a item"):
                st.write(resultado_items)

            resultado_flow = chat.check_vulnerability_per_item("data-flow", docs_para_analise)
            with st.expander(f"🔍 Resultado da Análise do fluxo de dados"):
                st.write(resultado_flow)
        






