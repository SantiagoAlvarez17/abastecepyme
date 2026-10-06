import { DependencyRepository, CreateDependencyDTO } from '../../domain/interfaces/DependencyRepository';
import { Dependency } from '../../domain/entities/Dependency';

export class ApiDependencyRepository implements DependencyRepository {
  private readonly baseUrl = 'http://localhost:8000/dependencies'; // Adjust for production

  async register(dependency: CreateDependencyDTO): Promise<Dependency> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dependency),
    });
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'Error al registrar dependencia');
    }
    return response.json();
  }
}
