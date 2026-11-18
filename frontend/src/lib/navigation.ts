import { ClipboardList, Factory, LayoutDashboard, type LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  role: string;
  icon: LucideIcon;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Operación",
    items: [{ href: "/tablero", label: "Tablero", role: "Gerencia de operaciones", icon: LayoutDashboard }],
  },
  {
    title: "Vistas por rol",
    items: [
      { href: "/compras", label: "Compras", role: "Responsable de compras", icon: ClipboardList },
      { href: "/produccion", label: "Producción", role: "Coordinador de producción", icon: Factory },
    ],
  },
];

export const NAV_ITEMS: NavItem[] = NAV_SECTIONS.flatMap((section) => section.items);
