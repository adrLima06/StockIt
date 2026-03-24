import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { 
  Package, 
  TrendingUp, 
  AlertTriangle, 
  DollarSign,
  ArrowUp,
  ArrowDown
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

// Mock data
const vendasSemanais = [
  { dia: "Seg", vendas: 12, valor: 1200 },
  { dia: "Ter", vendas: 19, valor: 1900 },
  { dia: "Qua", vendas: 15, valor: 1500 },
  { dia: "Qui", vendas: 22, valor: 2200 },
  { dia: "Sex", vendas: 28, valor: 2800 },
  { dia: "Sáb", vendas: 35, valor: 3500 },
  { dia: "Dom", vendas: 20, valor: 2000 },
];

const produtosBaixoEstoque = [
  { nome: "Caneta Azul", estoque: 5, minimo: 20 },
  { nome: "Caderno A4", estoque: 3, minimo: 10 },
  { nome: "Borracha Branca", estoque: 8, minimo: 15 },
];

export function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Visão geral do seu negócio</p>
      </div>

      {/* Cards de Indicadores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Produtos em Estoque
            </CardTitle>
            <Package className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">247</div>
            <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
              <ArrowUp className="h-3 w-3 text-green-500" />
              <span className="text-green-500">12%</span> vs. mês anterior
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Vendas do Mês
            </CardTitle>
            <DollarSign className="h-5 w-5 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">R$ 45.231</div>
            <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
              <ArrowUp className="h-3 w-3 text-green-500" />
              <span className="text-green-500">23%</span> vs. mês anterior
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Orçamentos Pendentes
            </CardTitle>
            <TrendingUp className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">8</div>
            <p className="text-xs text-gray-500 mt-2">
              Aguardando finalização
            </p>
          </CardContent>
        </Card>

        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-orange-900">
              Alertas de Estoque
            </CardTitle>
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-900">3</div>
            <p className="text-xs text-orange-700 mt-2">
              Produtos abaixo do mínimo
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Vendas Semanais */}
        <Card>
          <CardHeader>
            <CardTitle>Vendas da Semana</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={vendasSemanais}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="dia" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb' }}
                  formatter={(value) => [`${value} vendas`, 'Total']}
                />
                <Bar dataKey="vendas" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Produtos com Baixo Estoque */}
        <Card className="border-orange-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Produtos Abaixo do Estoque Mínimo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {produtosBaixoEstoque.map((produto, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <div>
                    <p className="font-medium text-gray-900">{produto.nome}</p>
                    <p className="text-sm text-gray-600">
                      Estoque: <span className="text-orange-600 font-semibold">{produto.estoque}</span> / Mínimo: {produto.minimo}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-orange-600 font-medium">CRÍTICO</p>
                    <p className="text-xs text-gray-500">Repor agora</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de Faturamento Mensal */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Faturamento dos Últimos 6 Meses</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[
              { mes: "Out", valor: 28500 },
              { mes: "Nov", valor: 32100 },
              { mes: "Dez", valor: 41200 },
              { mes: "Jan", valor: 35800 },
              { mes: "Fev", valor: 38900 },
              { mes: "Mar", valor: 45231 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="mes" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb' }}
                formatter={(value: number) => [`R$ ${value.toLocaleString('pt-BR')}`, 'Faturamento']}
              />
              <Line type="monotone" dataKey="valor" stroke="#10b981" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}