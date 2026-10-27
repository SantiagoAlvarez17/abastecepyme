"use client";

import { useState } from "react";
import { Network } from "lucide-react";
import { CatalogTable } from "@/components/catalog/CatalogTable";
import { DependencyForm } from "@/components/catalog/DependencyForm";
import { ElementDialog } from "@/components/catalog/ElementDialog";
import { ElementForm } from "@/components/catalog/ElementForm";
import { DependencyGraph } from "@/components/graph/DependencyGraph";
import { Card } from "@/components/ui/Card";
import { CatalogGate } from "@/components/ui/CatalogGate";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { TYPE_LABEL_PLURAL, TYPE_ORDER } from "@/lib/business-language";
import type { ElementDTO } from "@/lib/types";

export default function ComprasPage() {
  const [selected, setSelected] = useState<ElementDTO | null>(null);

  return (
    <>
      <PageHeader
        title="Catálogo de abastecimiento"
        description="Registre proveedores, insumos y productos finales, y defina qué necesita cada uno para producirse."
      />
      <CatalogGate>
        {(graph) => (
          <div className="space-y-8">
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {TYPE_ORDER.map((tipo) => (
                <StatCard
                  key={tipo}
                  tone={tipo}
                  label={TYPE_LABEL_PLURAL[tipo]}
                  value={graph.nodes.filter((n) => n.element_type === tipo).length}
                />
              ))}
              <StatCard label="Dependencias" value={graph.edges.length} hint="relaciones “para producir X necesito Y”" />
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <ElementForm graph={graph} />
              <DependencyForm graph={graph} />
            </section>

            <Card
              title="Red de dependencias"
              description="Haga clic en un elemento para resaltar lo que necesita y quién lo necesita. Use la rueda del mouse para acercar."
              icon={Network}
            >
              <DependencyGraph graph={graph} />
            </Card>

            <CatalogTable graph={graph} onSelect={setSelected} />
            <ElementDialog element={selected} graph={graph} onClose={() => setSelected(null)} />
          </div>
        )}
      </CatalogGate>
    </>
  );
}