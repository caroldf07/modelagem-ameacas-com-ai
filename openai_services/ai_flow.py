from openai import OpenAI
import base64

class Chat:

    def __init__(self, openai_api_key, model):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def load_prompt(self, filename):
        try:
            with open('prompts/' + filename, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            return conteudo
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {filename}")
            return None
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None
    
    def read_architecture(self, uploaded_file): 

        document = base64.b64encode(uploaded_file.read()).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Você é um agente especialista em arquitetura de sistemas e irá receber uma imagem de arquitetura para análise geral.
                            Seus objetivos são:
                            1. Interpretar a arquitetura e montar uma lista de componentes de cada elemento presente na imagem. Exemplo: AWS - S3, AWS - EC2, AWS - ECR, AWS - Lambda.
                            2. Explicar o que cada componente faz. Exemplo: AWS - S3: serviço de armazenamento em nuvem de arquivos.
                            3. Explicar o fluxo da aplicação apresentada com base na imagem.
                            ⚠️ Responda exclusivamente no formato JSON, utilizando as seguintes chaves:

                            {{
                            "componentes_identificados": [ "AWS - S3", "AWS - EC2", ... ],
                            "descricao_componentes": {{
                                "AWS - S3": "Serviço de armazenamento de objetos em nuvem...",
                                "AWS - EC2": "Serviço de computação elástica para hospedar aplicações..."
                            }},
                            "fluxo_aplicacao": "Descreva aqui o fluxo de como os componentes interagem entre si com base nas setas e estrutura da imagem."
                            }}
                            """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{document}"
                        }
                    }
                ]
            }

        ]
        stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        
        response = stream.choices[0].message.content
        return response
    
    def check_vulnerability_per_item(self, analysis_type, content):

        """
        Faz análise STRIDE baseada em conteúdo retornado da busca.
        
        Parâmetros:
            analysis_type (str): 'items' ou 'data-flow'
            content (list[dict]): Lista com chaves 'id' e 'conteudo'
        """
        # Construir string formatada para o prompt
        blocos_documento = []
        for doc in content:
            bloco = f"### Documento: {doc['id']}\n{doc['conteudo']}\n"
            blocos_documento.append(bloco)

        content_string = "\n---\n".join(blocos_documento)

        prompt = f"""
            Você está prestes a realizar uma análise de segurança com base nos documentos da OWASP relacionados à metodologia STRIDE.

            Abaixo estão os documentos relevantes que contêm diretrizes sobre ameaças e mitigações:

            {content_string}

            Existem dois tipos de análise possíveis (entre parênteses está o parâmetro da análise):
            1. Item a item, analisando cada componente isolado da arquitetura. (`items`)
            2. Análise do fluxo de dados entre componentes. (`data-flow`)

            Com base no conteúdo acima, realize a análise do tipo **{analysis_type}** e forneça:
            - As ameaças STRIDE relevantes
            - As justificativas técnicas
            - Recomendações de mitigação
            - E, se possível, uma organização em tópicos por componente ou interação.
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        
        response = stream.choices[0].message.content
        return response



        

        