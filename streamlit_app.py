import streamlit as st
from openai import OpenAI
import os
import base64

# Show title and description.
st.title("📄 Análise de Vulnerabilidade em Arquitetura de Software")
st.write(
    "Faça o upload da sua arquitetura de software em jpeg, png ou pdf e receba o relatório de vulnerabilidades que ela possa ter."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.info("Insira sua OpenAI API key para continuar", icon="🗝️")
    st.info("Importante que a sua chave tenha acesso ao modelo `o4-mini-2025-04-16`", icon="ℹ️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Faça o upload da sua arquitetura (.pdf/.jpeg/.png)", type=("pdf", "jpeg", "png")
    )

    if uploaded_file:

        # Process the uploaded file and question.
        document = base64.b64encode(uploaded_file.read()).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type":"text", "text": f""" Você é um agente especialista em arquitetura de sistemas e irá receber uma imagem de arquitetura para análise geral.
                     Seus objetivos são:
                     1. Interpretar a arquitetura e montar uma lista de componentes de cada elemento presente na imagem. Exemplo: AWS - S3, AWS - EC2, AWS - ECR, AWS - Lambda
                     2. Explicar o que cada componente faz. Exemplo: AWS - S3 : Storage em nuvem de arquivos... 
                     3. Explicar o fluxo da aplicação apresentada. Sendo a imagem da architetura: {uploaded_file.name}"""
                    },
                     {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{document}",
                            },
                    },
                ]
            }
        ]        
        with st.spinner('Analisando arquitetura... Por favor, aguarde.'):
            stream = client.chat.completions.create(
                model="o4-mini-2025-04-16",
                messages=messages,
            )
        
        # TODO: Alterar o prompt para que o retorno seja no formato que a lib de análise da OWASP precisa pra rodar.
        # TODO: Alterar o retorno para trazer o relatório de vulnerabilidades usando a metodologia STRIDE como base.
        # TODO: Incluir botão para download do relatório gerado em pdf.
        
        st.write(stream.choices[0].message.content)
        st.success("Análise concluída com sucesso!", icon="✅")
