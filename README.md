# 🌿 Haber - Detecção de Doenças em Folhas de Soja

Sistema web desenvolvido em Python/Streamlit para identificação automática de doenças em folhas de soja usando Deep Learning.

## 🎯 Principais Funcionalidades
- Identificação de 10 doenças comuns em folhas de soja
- Upload de imagens via interface intuitiva
- Geolocalização inteligente com múltiplas opções (EXIF, IP, manual)
- Mapeamento de ocorrências para análise regional
- Interface responsiva otimizada para dispositivos móveis

## 🔬 Doenças Identificadas
- Mossaic Virus
- Southern Blight
- Sudden Death Syndrome
- Yellow Mosaic
- Bacterial Blight
- Brown Spot
- Crestamento
- Ferrugem
- Powdery Mildew
- Septoria

## 🧠 Tecnologias
- Deep Learning com InceptionV3
- Streamlit para interface web
- Folium para visualização geográfica
- Processamento de imagens com PIL
- Geolocalização multi-fonte

## 📱 Compatibilidade
- Desktop (Windows, Linux, Mac)
- Dispositivos móveis (iOS, Android)
- Navegadores modernos

## 🚀 Diferenciais
- Interface dark mode moderna
- Sistema de login integrado
- Feedback visual em tempo real
- Recomendações personalizadas por região
- Documentação detalhada de doenças

Desenvolvido como parte de projeto de TCC, focando na acessibilidade e precisão para produtores rurais.

## 🛠️ Instalação e Uso

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Configuração do Ambiente
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/haber.git
cd haber
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executando o Projeto
1. Inicie o servidor Streamlit:
```bash
streamlit run app.py
```

2. Acesse a aplicação em seu navegador:
```
http://localhost:8501
```

## 📝 Como Usar
1. Faça login com suas credenciais
2. Faça upload da imagem da folha de soja
3. Aguarde a análise automática
4. Verifique o resultado e as recomendações

## 👥 Contribuição
Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de submeter pull requests.

## 📄 Licença
Este projeto está licenciado sob a [Licença MIT](LICENSE).

## 📁 Estrutura do Projeto

```
haber/
├── app.py                 # Arquivo principal da aplicação
├── requirements.txt       # Dependências do projeto
├── README.md             # Documentação do projeto
├── images/               # Imagens estáticas do sistema
│   └── haber.png        # Logo do projeto
├── utils/               # Módulos utilitários
│   └── doencas.py      # Gerenciamento de informações sobre doenças
└── paginas/            # Páginas da aplicação
    ├── doencas.py      # Página com catálogo de doenças
    ├── modelo.py       # Página com informações técnicas do modelo
    └── historico.py    # Página de histórico de análises
```

### 📂 Descrição dos Componentes

- `app.py`: Contém a lógica principal da aplicação, incluindo:
  - Sistema de autenticação
  - Processamento de imagens
  - Geolocalização multi-fonte
  - Interface principal

- `utils/doencas.py`: Gerencia o catálogo de doenças com:
  - Descrições detalhadas
  - Recomendações de tratamento
  - Informações técnicas

- `paginas/`:
  - `doencas.py`: Exibe catálogo completo de doenças e tratamentos
  - `modelo.py`: Documentação técnica do modelo de IA
  - `historico.py`: Registro de análises anteriores

### 🔄 Fluxo de Dados

1. Upload da imagem → Processamento → Análise pelo modelo
2. Extração de metadados → Geolocalização → Contextualização regional
3. Resultado → Recomendações personalizadas → Registro no histórico

