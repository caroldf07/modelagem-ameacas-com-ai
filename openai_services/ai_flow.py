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
    
    def check_vulnerability_per_item(self):
        pass
    
    def check_vulnerability_data_flow(self):
        pass