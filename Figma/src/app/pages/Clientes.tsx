import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { 
  Users, 
  Plus, 
  Search,
  MapPin,
  Building2,
  Phone,
  Mail
} from "lucide-react";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { toast } from "sonner";

// Mock data
const clientesIniciais = [
  { 
    id: 1, 
    nome: "João Silva", 
    cpf_cnpj: "123.456.789-00",
    email: "joao@email.com",
    telefone: "(11) 98765-4321",
    endereco: "Rua das Flores, 123",
    cidade: "São Paulo",
    uf: "SP"
  },
  { 
    id: 2, 
    nome: "Maria Santos", 
    cpf_cnpj: "987.654.321-00",
    email: "maria@email.com",
    telefone: "(11) 91234-5678",
    endereco: "Av. Paulista, 1000",
    cidade: "São Paulo",
    uf: "SP"
  },
  { 
    id: 3, 
    nome: "Empresa ABC Ltda", 
    cpf_cnpj: "12.345.678/0001-99",
    email: "contato@empresaabc.com",
    telefone: "(11) 3333-4444",
    endereco: "Rua Comercial, 500",
    cidade: "São Paulo",
    uf: "SP"
  },
];

type Cliente = typeof clientesIniciais[0];

export function Clientes() {
  const [clientes, setClientes] = useState(clientesIniciais);
  const [busca, setBusca] = useState("");
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [modalNovoCliente, setModalNovoCliente] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    nome: "",
    cpf_cnpj: "",
    email: "",
    telefone: "",
    cep: "",
    endereco: "",
    numero: "",
    complemento: "",
    bairro: "",
    cidade: "",
    uf: ""
  });

  const clientesFiltrados = clientes.filter(c => 
    c.nome.toLowerCase().includes(busca.toLowerCase()) ||
    c.cpf_cnpj.includes(busca)
  );

  const consultarCEP = async () => {
    if (!formData.cep || formData.cep.length < 8) {
      toast.error("CEP inválido");
      return;
    }

    try {
      // Mock da API BrasilAPI
      toast.info("Consultando CEP...");
      
      // Simulação de resposta da API
      setTimeout(() => {
        setFormData(prev => ({
          ...prev,
          endereco: "Avenida Paulista",
          bairro: "Bela Vista",
          cidade: "São Paulo",
          uf: "SP"
        }));
        toast.success("Endereço preenchido automaticamente!");
      }, 1000);
    } catch (error) {
      toast.error("Erro ao consultar CEP");
    }
  };

  const consultarCNPJ = async () => {
    if (!formData.cpf_cnpj || formData.cpf_cnpj.length < 14) {
      toast.error("CNPJ inválido");
      return;
    }

    try {
      // Mock da API BrasilAPI
      toast.info("Consultando CNPJ...");
      
      // Simulação de resposta da API
      setTimeout(() => {
        setFormData(prev => ({
          ...prev,
          nome: "Empresa Exemplo S.A.",
          email: "contato@exemplo.com.br",
          telefone: "(11) 3000-0000"
        }));
        toast.success("Dados da empresa preenchidos automaticamente!");
      }, 1000);
    } catch (error) {
      toast.error("Erro ao consultar CNPJ");
    }
  };

  const salvarCliente = () => {
    if (!formData.nome || !formData.cpf_cnpj) {
      toast.error("Preencha os campos obrigatórios");
      return;
    }

    const novoCliente: Cliente = {
      id: clientes.length + 1,
      nome: formData.nome,
      cpf_cnpj: formData.cpf_cnpj,
      email: formData.email,
      telefone: formData.telefone,
      endereco: `${formData.endereco}, ${formData.numero}`,
      cidade: formData.cidade,
      uf: formData.uf
    };

    setClientes(prev => [...prev, novoCliente]);
    toast.success(`Cliente ${formData.nome} cadastrado com sucesso!`);
    setModalNovoCliente(false);
    setFormData({
      nome: "",
      cpf_cnpj: "",
      email: "",
      telefone: "",
      cep: "",
      endereco: "",
      numero: "",
      complemento: "",
      bairro: "",
      cidade: "",
      uf: ""
    });
  };

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clientes</h1>
          <p className="text-gray-600 mt-1">Cadastro e consulta de clientes</p>
        </div>
        
        <Dialog open={modalNovoCliente} onOpenChange={setModalNovoCliente}>
          <DialogTrigger asChild>
            <Button className="bg-emerald-600 hover:bg-emerald-700">
              <Plus size={18} className="mr-2" />
              Novo Cliente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Cadastrar Novo Cliente</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              {/* Dados Principais */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <Label>Nome / Razão Social *</Label>
                    <Input 
                      placeholder="Nome completo ou razão social"
                      value={formData.nome}
                      onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                    />
                  </div>
                  
                  <div>
                    <Label>CPF / CNPJ *</Label>
                    <div className="flex gap-2">
                      <Input 
                        placeholder="000.000.000-00"
                        value={formData.cpf_cnpj}
                        onChange={(e) => setFormData(prev => ({ ...prev, cpf_cnpj: e.target.value }))}
                      />
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={consultarCNPJ}
                        title="Consultar CNPJ na Receita Federal"
                      >
                        <Building2 size={16} />
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Clique no ícone para buscar dados do CNPJ
                    </p>
                  </div>

                  <div>
                    <Label>Telefone</Label>
                    <div className="flex gap-2">
                      <Phone size={18} className="text-gray-400 mt-2" />
                      <Input 
                        placeholder="(00) 00000-0000"
                        value={formData.telefone}
                        onChange={(e) => setFormData(prev => ({ ...prev, telefone: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="col-span-2">
                    <Label>E-mail</Label>
                    <div className="flex gap-2">
                      <Mail size={18} className="text-gray-400 mt-2" />
                      <Input 
                        type="email"
                        placeholder="email@exemplo.com"
                        value={formData.email}
                        onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Endereço */}
              <div className="border-t pt-4">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <MapPin size={18} />
                  Endereço
                </h3>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label>CEP</Label>
                      <div className="flex gap-2">
                        <Input 
                          placeholder="00000-000"
                          value={formData.cep}
                          onChange={(e) => setFormData(prev => ({ ...prev, cep: e.target.value }))}
                        />
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={consultarCEP}
                          title="Consultar CEP"
                        >
                          <Search size={16} />
                        </Button>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Preenche endereço automaticamente
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4">
                    <div className="col-span-3">
                      <Label>Rua / Avenida</Label>
                      <Input 
                        placeholder="Nome da rua"
                        value={formData.endereco}
                        onChange={(e) => setFormData(prev => ({ ...prev, endereco: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Número</Label>
                      <Input 
                        placeholder="Nº"
                        value={formData.numero}
                        onChange={(e) => setFormData(prev => ({ ...prev, numero: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Complemento</Label>
                      <Input 
                        placeholder="Apto, Sala, etc."
                        value={formData.complemento}
                        onChange={(e) => setFormData(prev => ({ ...prev, complemento: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>Bairro</Label>
                      <Input 
                        placeholder="Bairro"
                        value={formData.bairro}
                        onChange={(e) => setFormData(prev => ({ ...prev, bairro: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="col-span-2">
                      <Label>Cidade</Label>
                      <Input 
                        placeholder="Cidade"
                        value={formData.cidade}
                        onChange={(e) => setFormData(prev => ({ ...prev, cidade: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label>UF</Label>
                      <Input 
                        placeholder="SP"
                        maxLength={2}
                        value={formData.uf}
                        onChange={(e) => setFormData(prev => ({ ...prev, uf: e.target.value.toUpperCase() }))}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Button 
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                onClick={salvarCliente}
              >
                Salvar Cliente
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de Clientes */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input 
                  placeholder="Buscar por nome ou CPF/CNPJ..." 
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
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF/CNPJ</TableHead>
                  <TableHead>Telefone</TableHead>
                  <TableHead>Cidade</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clientesFiltrados.map((cliente) => (
                  <TableRow 
                    key={cliente.id}
                    className={`cursor-pointer ${
                      clienteSelecionado?.id === cliente.id ? 'bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setClienteSelecionado(cliente)}
                  >
                    <TableCell className="font-medium">{cliente.nome}</TableCell>
                    <TableCell className="font-mono text-sm">{cliente.cpf_cnpj}</TableCell>
                    <TableCell>{cliente.telefone}</TableCell>
                    <TableCell>{cliente.cidade}/{cliente.uf}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Painel de Detalhes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users size={20} />
              Detalhes do Cliente
            </CardTitle>
          </CardHeader>
          <CardContent>
            {clienteSelecionado ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-bold text-lg text-gray-900">{clienteSelecionado.nome}</h3>
                  <p className="text-sm text-gray-500 font-mono">{clienteSelecionado.cpf_cnpj}</p>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <Mail className="text-gray-400 mt-0.5" size={18} />
                    <div>
                      <p className="text-xs text-gray-500">E-mail</p>
                      <p className="font-medium">{clienteSelecionado.email}</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <Phone className="text-gray-400 mt-0.5" size={18} />
                    <div>
                      <p className="text-xs text-gray-500">Telefone</p>
                      <p className="font-medium">{clienteSelecionado.telefone}</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <MapPin className="text-gray-400 mt-0.5" size={18} />
                    <div>
                      <p className="text-xs text-gray-500">Endereço</p>
                      <p className="font-medium">{clienteSelecionado.endereco}</p>
                      <p className="text-sm text-gray-600">
                        {clienteSelecionado.cidade}/{clienteSelecionado.uf}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <Button variant="outline" className="w-full">
                    Editar Cliente
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Users size={48} className="mx-auto mb-3 opacity-50" />
                <p>Selecione um cliente da lista para ver os detalhes</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
