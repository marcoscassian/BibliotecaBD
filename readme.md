````markdown
# Sistema de Biblioteca - db_trabalho3B

## Sobre o Projeto
Este é um sistema de gerenciamento de biblioteca desenvolvido para a disciplina **Banco de Dados** do 3º ano de **Informática para Internet**.  
O projeto permite cadastrar, visualizar, editar e excluir registros de:

- **Autores**
- **Editoras**
- **Gêneros**
- **Usuários**
- **Livros**
- **Empréstimos**

O sistema foi desenvolvido com **Flask**, **SQLAlchemy** e banco de dados **MySQL**, integrando conceitos de CRUD, relacionamentos e boas práticas de desenvolvimento web.

---

## Funcionalidades

- Cadastro de autores, editoras, gêneros, livros e usuários.
- Registro de empréstimos de livros, com controle de status: `pendente`, `devolvido` e `atrasado`.
- Relacionamentos configurados entre tabelas (ex.: um livro possui autor, gênero e editora; um empréstimo pertence a um usuário e a um livro).
- Interface simples para visualização e manipulação de dados através de formulários HTML.

---

## Tecnologias Utilizadas

- **Python 3**
- **Flask**
- **SQLAlchemy**
- **MySQL / Workbench**
- **HTML e CSS**

---

## Como Rodar o Projeto

1. **Crie o banco de dados no MySQL**  
Abra o Workbench e execute `db_trabalho3B.sql` para criar o banco e todas as tabelas.

2. **Crie e ative o ambiente virtual (opcional, mas recomendado):**
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
````

3. **Instale as dependências:**

```bash
pip install -r requirements.md
```

4. **Execute o sistema:**

```bash
python app.py
```

5. **Acesse no navegador:**

```
http://127.0.0.1:5000/
```

---

## Desenvolvedores

Atividade desenvolvida por:

* Fabian
* Ludimila
* Marcos
* Ícaro

Sob orientação do professor Hugo Wendell.

---