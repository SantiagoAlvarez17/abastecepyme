import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AppShell } from "@/components/layout/AppShell";
import { CatalogProvider } from "@/context/CatalogContext";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "AbastecePyme",
  description: "Control de abastecimiento y dependencias de producción",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={inter.variable}>
      <body className="antialiased">
        <CatalogProvider>
          <AppShell>{children}</AppShell>
        </CatalogProvider>
      </body>
    </html>
  );
}