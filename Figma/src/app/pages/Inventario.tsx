import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { 
  Package, 
  Plus, 
  Search,
  TrendingUp,
  TrendingDown,
  AlertTriangle
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
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Label } from "../components/ui/label";
import { toast } from "sonner";

// Mock data
const produtosIniciais = [
  { 
    id: 1, 
    codigo: "001", 
    nome: "Caneta Azul", 
    categoria: "Papelaria",
    estoque: 5, 
    estoque_minimo: 20,
    preco: 2.50,
    reservado: 2,
    movimentacao: [
      { dia: "15/03", qtd: 12 },
      { dia: "16/03", qtd: 10 },
      { dia: "17/03", qtd: 8 },
      { dia: "18/03", qtd: 7 },
      { dia: "19/03", qtd: 5 },
    ]
  },
  { 
    id: 2, 
    codigo: "002", 
    nome: "Caderno A4", 
    categoria: "Papelaria",
    estoque: 3, 
    estoque_minimo: 10,
    preco: 15.90,
    reservado: 1,
    movimentacao: [
      { dia: "15/03", qtd: 8 },
      { dia: "16/03", qtd: 7 },
      { dia: "17/03", qtd: 5 },
      { dia: "18/03", qtd: 4 },
      { dia: "19/03", qtd: 3 },
    ]
  },
  { 
    id: 3, 
    codigo: "003", 
    nome: "Borracha Branca", 
    categoria: "Papelaria",
    estoque: 8, 
    estoque_minimo: 15,
    preco: 1.20,
    reservado: 0,
    movimentacao: [
      { dia: "15/03", qtd: 15 },
      { dia: "16/03", qtd: 12 },
      { dia: "17/03", qtd: 10 },
      { dia: "18/03", qtd: 9 },
      { dia: "19/03", qtd: 8 },
    ]
  },
  { 
    id: 4, 
    codigo: "004", 
    nome: "Lápis HB", 
    categoria: "Papelaria",
    estoque: 45, 
    estoque_minimo: 30,
    preco: 1.50,
    reservado: 5,
    movimentacao: [
      { dia: "15/03", qtd: 50 },
      { dia: "16/03", qtd: 48 },
      { dia: "17/03", qtd: 47 },
      { dia: "18/03", qtd: 46 },
      { dia: "19/03", qtd: 45 },
    ]
  },
  { 
    id: 5, 
    codigo: "005", 
    nome: "Régua 30cm", 
    categoria: "Papelaria",
    estoque: 22, 
    estoque_minimo: 15,
    preco: 3.50,
    reservado: 3,
    movimentacao: [
      { dia: "15/03", qtd: 25 },
      { dia: "16/03", qtd: 24 },
      { dia: "17/03", qtd: 23 },
      { dia: "18/03", qtd: 22 },
      { dia: "19/03", qtd: 22 },
    ]
  },
];

type Produto = typeof produtosIniciais[0];

export function Inventario() {
  const [produtos, setProdutos] = useState(produtosIniciais);
  const [busca, setBusca] = useState("");
  const [produtoSelecionado, setProdutoSelecionado] = useState<Produto | null>(null);
  const [modalNovoProduto, setModalNovoProduto] = useState(false);
  const [modalEntrada, setModalEntrada] = useState(false);
  const [quantidadeEntrada, setQuantidadeEntrada] = useState("");

  const produtosFiltrados = produtos.filter(p => 
    p.nome.toLowerCase().includes(busca.toLowerCase()) ||
    p.codigo.includes(busca)
  );

  const getStatusBadge = (produto: Produto) => {
    const disponivelReal = produto.estoque - produto.reservado;
    if (produto.estoque < produto.estoque_minimo) {
      return <Badge variant="destructive" className="flex items-center gap-1">
        <AlertTriangle size={12} />
        CRÍTICO
      </Badge>;
    }
    if (disponivelReal < produto.estoque_minimo) {
      return <Badge className="bg-orange-500">ATENÇÃO</Badge>;
    }
    return <Badge className="bg-emerald-500">OK</Badge>;
  };

  const handleEntradaEstoque = () => {
    if (!produtoSelecionado || !quantidadeEntrada) return;
    
    const qtd = parseInt(quantidadeEntrada);
    setProdutos(prev => prev.map(p => 
      p.id === produtoSelecionado.id 
        ? { ...p, estoque: p.estoque + qtd }
        : p
    ));
    
    toast.success(`Entrada registrada: +${qtd} unidades de ${produtoSelecionado.nome}`);
    setModalEntrada(false);
    setQuantidadeEntrada("");
  };

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inventário</h1>
          <p className="text-gray-600 mt-1">Controle visual dos níveis de estoque</p>
        </div>
        
        <Dialog open={modalNovoProduto} onOpenChange={setModalNovoProduto}>
          <DialogTrigger asChild>
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              <Plus size={18} className="mr-2" />
              Novo Produto
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adicionar Novo Produto</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label>Código</Label>
                <Input placeholder="001" />
              </div>
              <div>
                <Label>Nome do Produto</Label>
                <Input placeholder="Ex: Caneta Azul" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Preço (R$)</Label>
                  <Input type="number" placeholder="0.00" />
                </div>
                <div>
                  <Label>Estoque Mínimo</Label>
                  <Input type="number" placeholder="10" />
                </div>
              </div>
              <Button className="w-full bg-emerald-600 hover:bg-emerald-700" onClick={() => {
                toast.success("Produto adicionado com sucesso!");
                setModalNovoProduto(false);
              }}>
                Salvar Produto
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tabela de Produtos */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input 
                  placeholder="Buscar por nome ou código..." 
                  className="pl-10"
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Produto</TableHead>
                  <TableHead className="text-center">Estoque</TableHead>
                  <TableHead className="text-center">Reservado</TableHead>
                  <TableHead className="text-center">Disponível</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {produtosFiltrados.map((produto) => {
                  const disponivelReal = produto.estoque - produto.reservado;
                  const isSelected = produtoSelecionado?.id === produto.id;
                  
                  return (
                    <TableRow 
                      key={produto.id}
                      className={`cursor-pointer ${
                        produto.estoque < produto.estoque_minimo 
                          ? 'bg-red-50 hover:bg-red-100' 
                          : isSelected
                          ? 'bg-blue-50'
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setProdutoSelecionado(produto)}
                    >
                      <TableCell className="font-mono">{produto.codigo}</TableCell>
                      <TableCell className="font-medium">{produto.nome}</TableCell>
                      <TableCell className="text-center">
                        {produto.estoque < produto.estoque_minimo ? (
                          <span className="text-red-600 font-semibold">{produto.estoque}</span>
                        ) : (
                          produto.estoque
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        {produto.reservado > 0 ? (
                          <Badge variant="outline" className="bg-blue-50">{produto.reservado}</Badge>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center font-semibold">
                        {disponivelReal}
                      </TableCell>
                      <TableCell className="text-center">
                        {getStatusBadge(produto)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            setProdutoSelecionado(produto);
                            setModalEntrada(true);
                          }}
                        >
                          <TrendingUp size={14} className="mr-1" />
                          Entrada
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Painel de Detalhes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package size={20} />
              Detalhes do Produto
            </CardTitle>
          </CardHeader>
          <CardContent>
            {produtoSelecionado ? (
              <div className="space-y-6">
                <div>
                  <h3 className="font-bold text-lg text-gray-900">{produtoSelecionado.nome}</h3>
                  <p className="text-sm text-gray-500">Código: {produtoSelecionado.codigo}</p>
                  <p className="text-lg font-semibold text-emerald-600 mt-2">
                    R$ {produtoSelecionado.preco.toFixed(2)}
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Estoque Total</span>
                    <span className="font-semibold">{produtoSelecionado.estoque}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <span className="text-sm text-gray-600">Reservado</span>
                    <span className="font-semibold text-blue-600">{produtoSelecionado.reservado}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                    <span className="text-sm text-gray-600">Disponível Real</span>
                    <span className="font-semibold text-emerald-600">
                      {produtoSelecionado.estoque - produtoSelecionado.reservado}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <span className="text-sm text-gray-600">Estoque Mínimo</span>
                    <span className="font-semibold text-orange-600">{produtoSelecionado.estoque_minimo}</span>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <TrendingDown size={16} />
                    Movimentação (5 dias)
                  </h4>
                  <ResponsiveContainer width="100%" height={150}>
                    <LineChart data={produtoSelecionado.movimentacao}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="dia" stroke="#6b7280" style={{ fontSize: '10px' }} />
                      <YAxis stroke="#6b7280" style={{ fontSize: '10px' }} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb' }}
                      />
                      <Line type="monotone" dataKey="qtd" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {produtoSelecionado.estoque < produtoSelecionado.estoque_minimo && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="text-red-600 mt-0.5" size={18} />
                      <div>
                        <p className="font-semibold text-red-900">Alerta de Reposição</p>
                        <p className="text-sm text-red-700 mt-1">
                          Este produto está abaixo do estoque mínimo. Reabasteça imediatamente!
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Package size={48} className="mx-auto mb-3 opacity-50" />
                <p>Selecione um produto da tabela para ver os detalhes</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Modal de Entrada de Estoque */}
      <Dialog open={modalEntrada} onOpenChange={setModalEntrada}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Entrada de Estoque</DialogTitle>
          </DialogHeader>
          {produtoSelecionado && (
            <div className="space-y-4 py-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">Produto</p>
                <p className="font-semibold text-lg">{produtoSelecionado.nome}</p>
                <p className="text-sm text-gray-500 mt-1">Estoque atual: {produtoSelecionado.estoque}</p>
              </div>
              <div>
                <Label>Quantidade a adicionar</Label>
                <Input 
                  type="number" 
                  placeholder="0"
                  value={quantidadeEntrada}
                  onChange={(e) => setQuantidadeEntrada(e.target.value)}
                />
              </div>
              <Button 
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                onClick={handleEntradaEstoque}
              >
                Confirmar Entrada
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}