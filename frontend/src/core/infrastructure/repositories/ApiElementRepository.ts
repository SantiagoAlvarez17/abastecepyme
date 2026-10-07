import { ElementRepository, CreateElementDTO } from '../../domain/interfaces/ElementRepository';
import { Element } from '../../domain/entities/Element';
import { ElementType } from '../../domain/enums/ElementType';

// Forma exacta que devuelve la API (snake_case)
interface ElementApiResponse {
  id: string;
  name: string;
  element_type: ElementType;
  is_active: boolean;
}

const toElement = (raw: ElementApiResponse): Element => ({
  id: raw.id,
  name: raw.name,
  elementType: raw.element_type,
  isActive: raw.is_active,
});

export class ApiElementRepository implements ElementRepository {
  private readonly baseUrl = 'http://localhost:8000/elements'; // Adjust for production

  async getAll(): Promise<Element[]> {
    const response = await fetch(this.baseUrl);
    if (!response.ok) {
      throw new Error('Error al obtener los elementos');
    }
    const data: ElementApiResponse[] = await response.json();
    return data.map(toElement);
  }

  async create(element: CreateElementDTO): Promise<Element> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(element),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'Error al crear elemento');
    }
    return toElement(await response.json());
  }
}
