import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { Inventario } from "./pages/Inventario";
import { Clientes } from "./pages/Clientes";
import { Vendas } from "./pages/Vendas";
import { Configuracoes } from "./pages/Configuracoes";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "inventario", Component: Inventario },
      { path: "clientes", Component: Clientes },
      { path: "vendas", Component: Vendas },
      { path: "configuracoes", Component: Configuracoes },
    ],
  },
]);
