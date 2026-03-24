import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { 
  Settings, 
  Database,
  Key,
  Save,
  RefreshCw
} from "lucide-react";
import { toast } from "sonner";

export function Configuracoes() {
  const handleSalvarConfiguracoes = () => {
    toast.success("Configurações salvas com sucesso!");
  };

  const handleTestarConexao = () => {
    toast.info("Testando conexão...");
    setTimeout(() => {
      toast.success("Conexão estabelecida com sucesso!");
    }, 1500);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
        <p className="text-gray-600 mt-1">Ajustes de banco de dados e APIs</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configurações de Banco de Dados */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database size={20} />
              Banco de Dados
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Host do Servidor</Label>
              <Input placeholder="localhost" defaultValue="localhost" />
            </div>
            <div>
              <Label>Porta</Label>
              <Input placeholder="5432" defaultValue="5432" />
            </div>
            <div>
              <Label>Nome do Banco</Label>
              <Input placeholder="stockit_db" defaultValue="stockit_db" />
            </div>
            <div>
              <Label>Usuário</Label>
              <Input placeholder="admin" defaultValue="admin" />
            </div>
            <div>
              <Label>Senha</Label>
              <Input type="password" placeholder="••••••••" />
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={handleTestarConexao}
              >
                <RefreshCw size={16} className="mr-2" />
                Testar Conexão
              </Button>
              <Button 
                className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                onClick={handleSalvarConfiguracoes}
              >
                <Save size={16} className="mr-2" />
                Salvar
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Configurações de APIs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key size={20} />
              Integração de APIs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>BrasilAPI - Consulta CEP</Label>
              <Input 
                placeholder="https://brasilapi.com.br/api/cep/v1/" 
                defaultValue="https://brasilapi.com.br/api/cep/v1/"
                disabled
              />
              <p className="text-xs text-gray-500 mt-1">
                API pública - não requer autenticação
              </p>
            </div>
            <div>
              <Label>BrasilAPI - Consulta CNPJ</Label>
              <Input 
                placeholder="https://brasilapi.com.br/api/cnpj/v1/" 
                defaultValue="https://brasilapi.com.br/api/cnpj/v1/"
                disabled
              />
              <p className="text-xs text-gray-500 mt-1">
                API pública - não requer autenticação
              </p>
            </div>

            <div className="pt-4 border-t">
              <h4 className="font-semibold mb-3">API Personalizada (Opcional)</h4>
              <div className="space-y-3">
                <div>
                  <Label>URL da API</Label>
                  <Input placeholder="https://sua-api.com.br" />
                </div>
                <div>
                  <Label>Token de Autenticação</Label>
                  <Input type="password" placeholder="••••••••" />
                </div>
              </div>
            </div>

            <Button 
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              onClick={handleSalvarConfiguracoes}
            >
              <Save size={16} className="mr-2" />
              Salvar Configurações
            </Button>
          </CardContent>
        </Card>

        {/* Configurações Gerais */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings size={20} />
              Configurações Gerais
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Nome da Empresa</Label>
              <Input placeholder="Minha Empresa Ltda" />
            </div>
            <div>
              <Label>CNPJ</Label>
              <Input placeholder="00.000.000/0001-00" />
            </div>
            <div>
              <Label>Tempo de Expiração de Orçamentos (minutos)</Label>
              <Input type="number" defaultValue="60" />
              <p className="text-xs text-gray-500 mt-1">
                Tempo até a reserva temporária expirar
              </p>
            </div>
            <div>
              <Label>Margem de Alerta de Estoque (%)</Label>
              <Input type="number" defaultValue="20" />
              <p className="text-xs text-gray-500 mt-1">
                Porcentagem do estoque mínimo para disparar alertas
              </p>
            </div>
            <Button 
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              onClick={handleSalvarConfiguracoes}
            >
              <Save size={16} className="mr-2" />
              Salvar Configurações
            </Button>
          </CardContent>
        </Card>

        {/* Informações do Sistema */}
        <Card>
          <CardHeader>
            <CardTitle>Informações do Sistema</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Versão do Sistema</span>
              <span className="font-semibold">1.0.0</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Última Atualização</span>
              <span className="font-semibold">19/03/2026</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Produtos Cadastrados</span>
              <span className="font-semibold">247</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Clientes Cadastrados</span>
              <span className="font-semibold">143</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Vendas do Mês</span>
              <span className="font-semibold text-emerald-600">R$ 45.231,00</span>
            </div>

            <div className="pt-4 mt-4 border-t">
              <Button variant="outline" className="w-full">
                Fazer Backup do Sistema
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
