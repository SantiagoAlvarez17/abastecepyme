import { ElementRepository, CreateElementDTO } from '../../domain/interfaces/ElementRepository';
import { Element } from '../../domain/entities/Element';

export class ApiElementRepository implements ElementRepository {
  private readonly baseUrl = 'http://localhost:8000/elements'; // Adjust for production

  async getAll(): Promise<Element[]> {
    const response = await fetch(this.baseUrl);
    if (!response.ok) {
      throw new Error('Error al obtener los elementos');
    }
    return response.json();
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
    return response.json();
  }
}
