# StockIt

O **Stock It!** é uma solução web moderna desenvolvida para microempreendedores que buscam controle total sobre seu inventário, clientes e vendas. O projeto utiliza uma interface baseada em componentes de alta fidelidade para garantir produtividade e integridade dos dados.

## 🚀 Tecnologias Principais
* **Frontend:** React.js com TypeScript (TSX).
* **Estilização:** Tailwind CSS & Shadcn/ui.
* **Ícones:** Lucide React.
* **Banco de Dados:** MySQL Server.
* **ORM:** Prisma (Interface entre o código e o banco).
* **Build Tool:** Vite.

## 📂 Estrutura do Projeto
A estrutura do repositório está organizada para separar a base visual da lógica de negócio:

* **/Figma**: Contém o protótipo visual inicial (PR01) e componentes de interface.
* **/src/app/pages**: Telas principais do sistema:
    * `Dashboard.tsx`: Indicadores e métricas rápidas.
    * `Inventario.tsx`: Gestão de produtos e alertas de estoque mínimo.
    * `Clientes.tsx`: Cadastro automatizado via APIs externas.
    * `Vendas.tsx`: Fluxo de orçamentos e baixa de estoque.
* **/src/app/components/ui**: Biblioteca de componentes visuais (Botões, Tabelas, Diálogos).

## 🛠️ Funcionalidades de Destaque
1.  **Reserva Temporária de Estoque:** Ao criar um orçamento, os itens são marcados como "reservados" no banco de dados para evitar vendas duplicadas.
2.  **Baixa Automática:** A confirmação de uma venda subtrai instantaneamente a quantidade do estoque físico.
3.  **Alerta de Reposição:** Notificações visuais automáticas para produtos que atingem o nível crítico de estoque.
4.  **Cadastro Inteligente:** Integração com **BrasilAPI** para preenchimento automático de endereços (CEP) e dados de empresas (CNPJ).

## 💻 Como Rodar o Projeto
1.  Clone o repositório:
    ```bash
    git clone https://github.com/adrlima06/stockit.git
    ```
2.  Instale as dependências:
    ```bash
    npm install
    ```
3.  Configure o arquivo `.env` com suas credenciais do **MySQL**.
4.  Inicie o servidor de desenvolvimento:
    ```bash
    npm run dev
    ```

##Cronograma de Versões

* **v0.1.0 (Atual):** Estrutura visual (Figma) e base (PR01) Adicionadas ao Projeto
