import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { 
  ShoppingCart, 
  Plus, 
  Search,
  Clock,
  CheckCircle,
  AlertTriangle,
  Trash2,
  FileText,
  User
} from "lucide-react";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../components/ui/table";
import { Badge } from "../components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "sonner";

// Mock data
const produtosDisponiveis = [
  { id: 1, codigo: "001", nome: "Caneta Azul", preco: 2.50, estoque: 5, reservado: 2 },
  { id: 2, codigo: "002", nome: "Caderno A4", preco: 15.90, estoque: 3, reservado: 1 },
  { id: 3, codigo: "003", nome: "Borracha Branca", preco: 1.20, estoque: 8, reservado: 0 },
  { id: 4, codigo: "004", nome: "Lápis HB", preco: 1.50, estoque: 45, reservado: 5 },
  { id: 5, codigo: "005", nome: "Régua 30cm", preco: 3.50, estoque: 22, reservado: 3 },
];

const clientesDisponiveis = [
  { id: 1, nome: "João Silva", cpf_cnpj: "123.456.789-00" },
  { id: 2, nome: "Maria Santos", cpf_cnpj: "987.654.321-00" },
  { id: 3, nome: "Empresa ABC Ltda", cpf_cnpj: "12.345.678/0001-99" },
];

type Orcamento = {
  id: string;
  cliente: string;
  itens: Array<{
    produto: string;
    quantidade: number;
    preco: number;
  }>;
  total: number;
  criado_em: Date;
  expira_em: Date;
  status: "pendente" | "finalizado" | "expirado";
};

export function Vendas() {
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([
    {
      id: "ORC-001",
      cliente: "João Silva",
      itens: [
        { produto: "Caneta Azul", quantidade: 2, preco: 2.50 },
        { produto: "Caderno A4", quantidade: 1, preco: 15.90 }
      ],
      total: 20.90,
      criado_em: new Date(Date.now() - 30 * 60 * 1000),
      expira_em: new Date(Date.now() + 30 * 60 * 1000),
      status: "pendente"
    }
  ]);

  const [modalNovoOrcamento, setModalNovoOrcamento] = useState(false);
  const [clienteSelecionado, setClienteSelecionado] = useState("");
  const [buscaProduto, setBuscaProduto] = useState("");
  const [itensOrcamento, setItensOrcamento] = useState<Array<{
    produto: typeof produtosDisponiveis[0];
    quantidade: number;
  }>>([]);

  // Atualizar cronômetros
  useEffect(() => {
    const interval = setInterval(() => {
      setOrcamentos(prev => 
        prev.map(orc => {
          if (orc.status === "pendente" && new Date() > orc.expira_em) {
            toast.warning(`Orçamento ${orc.id} expirou!`, {
              description: "A reserva foi liberada e o estoque está disponível novamente."
            });
            return { ...orc, status: "expirado" as const };
          }
          return orc;
        })
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const produtosFiltrados = produtosDisponiveis.filter(p => 
    p.nome.toLowerCase().includes(buscaProduto.toLowerCase()) ||
    p.codigo.includes(buscaProduto)
  );

  const adicionarItem = (produto: typeof produtosDisponiveis[0]) => {
    const disponivelReal = produto.estoque - produto.reservado;
    if (disponivelReal <= 0) {
      toast.error("Produto sem estoque disponível!");
      return;
    }

    const itemExistente = itensOrcamento.find(i => i.produto.id === produto.id);
    if (itemExistente) {
      if (itemExistente.quantidade >= disponivelReal) {
        toast.error("Quantidade máxima disponível atingida!");
        return;
      }
      setItensOrcamento(prev =>
        prev.map(i =>
          i.produto.id === produto.id
            ? { ...i, quantidade: i.quantidade + 1 }
            : i
        )
      );
    } else {
      setItensOrcamento(prev => [...prev, { produto, quantidade: 1 }]);
    }
    toast.success(`${produto.nome} adicionado ao orçamento`);
  };

  const removerItem = (produtoId: number) => {
    setItensOrcamento(prev => prev.filter(i => i.produto.id !== produtoId));
  };

  const atualizarQuantidade = (produtoId: number, quantidade: number) => {
    const item = itensOrcamento.find(i => i.produto.id === produtoId);
    if (!item) return;

    const disponivelReal = item.produto.estoque - item.produto.reservado;
    if (quantidade > disponivelReal) {
      toast.error("Quantidade indisponível!");
      return;
    }
    if (quantidade < 1) {
      removerItem(produtoId);
      return;
    }

    setItensOrcamento(prev =>
      prev.map(i =>
        i.produto.id === produtoId ? { ...i, quantidade } : i
      )
    );
  };

  const calcularTotal = () => {
    return itensOrcamento.reduce((acc, item) => 
      acc + (item.produto.preco * item.quantidade), 0
    );
  };

  const criarOrcamento = () => {
    if (!clienteSelecionado || itensOrcamento.length === 0) {
      toast.error("Selecione um cliente e adicione produtos!");
      return;
    }

    const novoOrcamento: Orcamento = {
      id: `ORC-${String(orcamentos.length + 1).padStart(3, '0')}`,
      cliente: clienteSelecionado,
      itens: itensOrcamento.map(item => ({
        produto: item.produto.nome,
        quantidade: item.quantidade,
        preco: item.produto.preco
      })),
      total: calcularTotal(),
      criado_em: new Date(),
      expira_em: new Date(Date.now() + 60 * 60 * 1000), // 1 hora
      status: "pendente"
    };

    setOrcamentos(prev => [...prev, novoOrcamento]);
    toast.success(`Orçamento ${novoOrcamento.id} criado com sucesso!`, {
      description: "Os itens foram reservados temporariamente."
    });

    // Limpar formulário
    setClienteSelecionado("");
    setItensOrcamento([]);
    setModalNovoOrcamento(false);
  };

  const finalizarVenda = (orcamento: Orcamento) => {
    setOrcamentos(prev =>
      prev.map(orc =>
        orc.id === orcamento.id ? { ...orc, status: "finalizado" as const } : orc
      )
    );

    toast.success(`Venda ${orcamento.id} finalizada com sucesso!`, {
      description: "Baixa automática de estoque realizada. PDF gerado.",
      action: {
        label: "Ver PDF",
        onClick: () => toast.info("Abrindo PDF da venda...")
      }
    });

    // Simular alerta de reposição
    setTimeout(() => {
      toast.warning("Alerta de Reposição", {
        description: "2 produtos atingiram o nível crítico de estoque.",
        action: {
          label: "Ver Inventário",
          onClick: () => window.location.href = "/inventario"
        }
      });
    }, 2000);
  };

  const getTempoRestante = (expiraEm: Date) => {
    const agora = new Date();
    const diff = expiraEm.getTime() - agora.getTime();
    
    if (diff <= 0) return "Expirado";
    
    const minutos = Math.floor(diff / 60000);
    const segundos = Math.floor((diff % 60000) / 1000);
    
    return `${minutos}:${String(segundos).padStart(2, '0')}`;
  };

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Orçamentos & Vendas</h1>
          <p className="text-gray-600 mt-1">Criação e conversão de pedidos</p>
        </div>
        
        <Dialog open={modalNovoOrcamento} onOpenChange={setModalNovoOrcamento}>
          <DialogTrigger asChild>
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              <Plus size={18} className="mr-2" />
              Novo Orçamento
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Criar Novo Orçamento</DialogTitle>
            </DialogHeader>
            <div className="space-y-6 py-4">
              {/* Seleção de Cliente */}
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <User size={16} />
                  Cliente *
                </Label>
                <Select value={clienteSelecionado} onValueChange={setClienteSelecionado}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clientesDisponiveis.map(cliente => (
                      <SelectItem key={cliente.id} value={cliente.nome}>
                        {cliente.nome} - {cliente.cpf_cnpj}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Busca de Produtos */}
              <div>
                <Label className="flex items-center gap-2 mb-2">
                  <ShoppingCart size={16} />
                  Adicionar Produtos
                </Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input 
                    placeholder="Buscar por nome ou código de barras..." 
                    className="pl-10"
                    value={buscaProduto}
                    onChange={(e) => setBuscaProduto(e.target.value)}
                  />
                </div>

                {buscaProduto && (
                  <div className="mt-2 border rounded-lg max-h-48 overflow-y-auto">
                    {produtosFiltrados.map(produto => {
                      const disponivelReal = produto.estoque - produto.reservado;
                      return (
                        <div 
                          key={produto.id}
                          className="p-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0 flex items-center justify-between"
                          onClick={() => adicionarItem(produto)}
                        >
                          <div className="flex-1">
                            <p className="font-medium">{produto.nome}</p>
                            <p className="text-sm text-gray-500">
                              Código: {produto.codigo} | 
                              Disponível: <span className={disponivelReal > 0 ? "text-emerald-600" : "text-red-600"}>
                                {disponivelReal}
                              </span>
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold text-emerald-600">
                              R$ {produto.preco.toFixed(2)}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Itens do Orçamento */}
              {itensOrcamento.length > 0 && (
                <div className="border rounded-lg p-4 bg-gray-50">
                  <h3 className="font-semibold mb-4">Itens Selecionados</h3>
                  <div className="space-y-3">
                    {itensOrcamento.map(item => (
                      <div key={item.produto.id} className="flex items-center gap-4 bg-white p-3 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium">{item.produto.nome}</p>
                          <p className="text-sm text-gray-500">R$ {item.produto.preco.toFixed(2)} cada</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => atualizarQuantidade(item.produto.id, item.quantidade - 1)}
                          >
                            -
                          </Button>
                          <Input 
                            type="number" 
                            value={item.quantidade}
                            onChange={(e) => atualizarQuantidade(item.produto.id, parseInt(e.target.value) || 0)}
                            className="w-16 text-center"
                          />
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => atualizarQuantidade(item.produto.id, item.quantidade + 1)}
                          >
                            +
                          </Button>
                        </div>
                        <p className="font-semibold w-24 text-right">
                          R$ {(item.produto.preco * item.quantidade).toFixed(2)}
                        </p>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => removerItem(item.produto.id)}
                        >
                          <Trash2 size={16} className="text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 pt-4 border-t flex items-center justify-between">
                    <p className="font-semibold text-lg">Total:</p>
                    <p className="font-bold text-2xl text-emerald-600">
                      R$ {calcularTotal().toFixed(2)}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => setModalNovoOrcamento(false)}
                >
                  Cancelar
                </Button>
                <Button 
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                  onClick={criarOrcamento}
                >
                  Criar Orçamento
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Orçamentos Pendentes */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock size={20} />
            Orçamentos Pendentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {orcamentos.filter(o => o.status === "pendente").map(orcamento => (
              <div key={orcamento.id} className="border rounded-lg p-4 bg-blue-50 border-blue-200">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-lg">{orcamento.id}</h3>
                    <p className="text-sm text-gray-600">Cliente: {orcamento.cliente}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Criado em: {orcamento.criado_em.toLocaleString('pt-BR')}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge className="bg-orange-500 mb-2">
                      <Clock size={12} className="mr-1" />
                      {getTempoRestante(orcamento.expira_em)}
                    </Badge>
                    <p className="font-bold text-2xl text-emerald-600">
                      R$ {orcamento.total.toFixed(2)}
                    </p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  {orcamento.itens.map((item, idx) => (
                    <div key={idx} className="flex justify-between text-sm bg-white p-2 rounded">
                      <span>{item.quantidade}x {item.produto}</span>
                      <span className="font-medium">R$ {(item.preco * item.quantidade).toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <Button 
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => finalizarVenda(orcamento)}
                  >
                    <CheckCircle size={16} className="mr-2" />
                    Finalizar Venda
                  </Button>
                  <Button variant="outline">
                    <FileText size={16} className="mr-2" />
                    Imprimir
                  </Button>
                </div>
              </div>
            ))}

            {orcamentos.filter(o => o.status === "pendente").length === 0 && (
              <div className="text-center py-12 text-gray-400">
                <ShoppingCart size={48} className="mx-auto mb-3 opacity-50" />
                <p>Nenhum orçamento pendente no momento</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Histórico de Vendas */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Vendas</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Data</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead className="text-center">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orcamentos.filter(o => o.status !== "pendente").map(orcamento => (
                <TableRow key={orcamento.id}>
                  <TableCell className="font-mono">{orcamento.id}</TableCell>
                  <TableCell>{orcamento.cliente}</TableCell>
                  <TableCell>{orcamento.criado_em.toLocaleDateString('pt-BR')}</TableCell>
                  <TableCell className="text-right font-semibold">
                    R$ {orcamento.total.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-center">
                    {orcamento.status === "finalizado" ? (
                      <Badge className="bg-emerald-500">
                        <CheckCircle size={12} className="mr-1" />
                        Finalizado
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-gray-500">
                        <AlertTriangle size={12} className="mr-1" />
                        Expirado
                      </Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
