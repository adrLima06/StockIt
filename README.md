# 📦 Stock It!

O **Stock It!** é uma solução web desenvolvida para microempreendedores que buscam controle total sobre seu inventário, clientes e vendas. O projeto utiliza uma interface baseada em componentes de alta fidelidade para garantir produtividade e integridade dos dados.

## 🚀 Tecnologias Principais
* **Frontend:** React.js com TypeScript (TSX)
* **Estilização:** Tailwind CSS & Shadcn/ui
* **Ícones:** Lucide React
* **Banco de Dados:** MySQL Server
* **ORM:** Prisma (Interface entre o código e o banco)
* **Build Tool:** Vite

## 📅 Cronograma de Versões
* **v0.1.0 (Atual):** Estrutura visual (Figma) e base (PR01) adicionadas ao projeto.

## 📂 Estrutura de Pastas e Arquivos
```text
app/
├── prisma/                  # Configurações e Migrations do Banco de Dados (MySQL)
├── public/                  # Ativos estáticos: Imagens, Ícones e Logotipos
└── src/                     # Código-fonte da aplicação
    ├── estilos/             # Estilização global e configurações do Tailwind CSS
    ├── app/                 # Núcleo da lógica React
    │   ├── componentes/     # Componentes React reutilizáveis
    │   │   └── ui/          # Elementos visuais baseados no Figma (Design System)
    │   ├── paginas/         # Telas: Dashboard, Inventário, Clientes e Vendas
    │   ├── servicos/        # Integrações (BrasilAPI) e chamadas ao Banco
    │   ├── tipos/           # Definições de tipos e interfaces do TypeScript
    │   └── utilitarios/     # Funções auxiliares (Formatadores e Validadores)
