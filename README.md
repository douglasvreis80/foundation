# API de Gerenciamento de Partidas e Jogadores

Esta é uma API desenvolvida em Flask para gerenciar partidas e jogadores, incluindo recursos para criar partidas, adicionar jogadores a elas e controlar a lotação de slots (principais, goleiros e espera).

## Funcionalidades
- **Gerenciamento de Partidas**: Criar partidas com slots configuráveis para jogadores principais, goleiros e lista de espera.
- **Gerenciamento de Jogadores**: Adicionar jogadores às partidas, garantindo que não haja duplicatas.
- **Controle de Slots**: Verifica automaticamente os slots disponíveis e organiza jogadores nos status "principais", "goleiros" ou "espera".

## Tecnologias Utilizadas
- Python
- Flask
- SQLAlchemy
- SQLite (banco de dados leve para persistência)

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   ```

2. Acesse o diretório do projeto:
   ```bash
   cd seu-repositorio
   ```

3. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Inicie o servidor:
   ```bash
   python app.py
   ```

5. A API estará disponível em: `http://127.0.0.1:5000`

## Endpoints

### **Partidas**

#### Criar uma nova partida
- **Endpoint**: `POST /partida`
- **Corpo da requisição (JSON)**:
  ```json
  {
    "nome": "Nome da Partida",
    "slots_primarios": 10,
    "slots_goleiros": 2,
    "slots_espera": 5
  }
  ```
- **Resposta de Sucesso (JSON)**:
  ```json
  {
    "status": "sucesso",
    "mensagem": "Partida criada com sucesso."
  }
  ```

### **Jogadores**

#### Adicionar um jogador a uma partida
- **Endpoint**: `POST /jogador`
- **Corpo da requisição (JSON)**:
  ```json
  {
    "nome": "Nome do Jogador",
    "posicao": "jogador",
    "partida_id": 1
  }
  ```
  - `posicao`: Pode ser `jogador` ou `goleiro`.

- **Restrições**:
  - Um jogador não pode ser adicionado mais de uma vez à mesma partida.
  - Slots respeitam a capacidade definida na criação da partida.

- **Resposta de Sucesso (JSON)**:
  ```json
  {
    "status": "sucesso",
    "mensagem": "Nome do Jogador adicionado como jogador."
  }
  ```

- **Resposta de Erro (JSON)**:
  ```json
  {
    "status": "erro",
    "mensagem": "O jogador Nome do Jogador já está registrado nesta partida."
  }
  ```

## Modelo de Dados

### Partida
| Campo            | Tipo    | Descrição                          |
|------------------|---------|----------------------------------|
| `id`             | Integer | Identificador único da partida      |
| `nome`           | String  | Nome da partida                  |
| `slots_primarios`| Integer | Quantidade de slots para jogadores principais |
| `slots_goleiros` | Integer | Quantidade de slots para goleiros |
| `slots_espera`   | Integer | Quantidade de slots para a lista de espera |

### Jogador
| Campo        | Tipo    | Descrição                          |
|--------------|---------|----------------------------------|
| `id`         | Integer | Identificador único do jogador     |
| `nome`       | String  | Nome do jogador                  |
| `posicao`    | String  | Posição: `jogador` ou `goleiro`    |
| `status`     | String  | Status: `principais`, `goleiros`, `espera` |
| `partida_id` | Integer | Referência à partida associada     |

## Contribuição

1. Faça um fork do projeto.
2. Crie uma branch para a sua feature: `git checkout -b minha-feature`
3. Commit suas mudanças: `git commit -m 'Minha nova feature'`
4. Dê um push na branch: `git push origin minha-feature`
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).

---
**Mantenedor**: Seu Nome ([seu-email@example.com](mailto:seu-email@example.com))

