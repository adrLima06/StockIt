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
  
## ⚙️ Funcionalidades Principais
1.  **Gestão de Estoque (Inventário)** Painel centralizado para controle de quantidades físicas, edição de preços de custo/venda e organização detalhada de todos os produtos cadastrados.
2.  **Alerta de Reposição Automática** Monitoramento inteligente que emite notificações visuais instantâneas quando um item atinge o limite mínimo de segurança configurado, evitando a falta de mercadoria.
3.  **Entrada de Mercadoria (Compra)** Módulo dedicado para registrar a chegada de novas unidades de fornecedores, permitindo a atualização automática do estoque e do histórico de custos.
4.  **Reserva Temporária de Itens** Bloqueio automático de produtos vinculados a orçamentos pendentes. Essa função garante a disponibilidade do item para o cliente interessado por um tempo determinado.
5.  **Emissão de PDF Profissional** Geração de orçamentos e outros personalizados e estilizados, prontos para impressão ou envio digital ao cliente.
6.  **Cálculo de Totais** Processamento automático de somas, aplicações de descontos e taxas, garantindo precisão absoluta no fechamento financeiro de cada pedido.
7.  **Cadastro Automatizado por API** Integração com a **BrasilAPI** para autopreenchimento de dados cadastrais. Ao digitar o CEP ou CNPJ, o sistema busca e preenche automaticamente os endereços e dados empresariais.
8.  **Histórico de Compras por Cliente** Registro completo de todas as transações realizadas por cada cliente, permitindo uma análise rápida do perfil de compra e fidelização.
9.  **Relatório de Movimentação** Log detalhado de auditoria que registra todas as entradas, saídas e ajustes manuais feitos no estoque, informando data, quantidade e motivo.
10. **Backup do Banco de Dados** Ferramenta de segurança para exportação integral dos dados do MySQL local, garantindo que as informações da empresa estejam protegidas contra falhas de hardware.
    
## 📂 Estrutura de Pastas e Arquivos
```text
app/
├── prisma/                  # Configurações e Migrations do Banco de Dados (MySQL)
├── public/                  # Ativos estáticos: Imagens, Ícones e Logotipos
└── src/                     # Código-fonte da aplicação
    ├── app/                 # Núcleo da lógica React
    │   ├── componentes/     # Componentes React reutilizáveis
    │   │   └── ui/          # Elementos visuais baseados no Figma (Design System)
    │   ├── paginas/         # Telas: Dashboard, Inventário, Clientes e Vendas
    │   ├── servicos/        # Integrações (BrasilAPI) e chamadas ao Banco
    │   ├── tipos/           # Definições de tipos e interfaces do TypeScript
    │   └── utilitarios/     # Funções auxiliares (Formatadores e Validadores)
    └── estilos/             # Estilização global e configurações do Tailwind CSS
