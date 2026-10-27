import { TYPE_LABEL_PLURAL, TYPE_ORDER } from "@/lib/business-language";
import type { ElementDTO } from "@/lib/types";

export const byTypeThenName = (a: ElementDTO, b: ElementDTO) =>
  TYPE_ORDER.indexOf(a.element_type) - TYPE_ORDER.indexOf(b.element_type) || a.name.localeCompare(b.name, "es");

export function OptionGroups({ elements }: Readonly<{ elements: ElementDTO[] }>) {
  return (
    <>
      {TYPE_ORDER.map((t) => {
        const items = elements.filter((e) => e.element_type === t);
        if (items.length === 0) return null;
        return (
          <optgroup key={t} label={TYPE_LABEL_PLURAL[t]}>
            {items.map((e) => (
              <option key={e.id} value={e.id}>
                {e.name}
              </option>
            ))}
          </optgroup>
        );
      })}
    </>
  );
}