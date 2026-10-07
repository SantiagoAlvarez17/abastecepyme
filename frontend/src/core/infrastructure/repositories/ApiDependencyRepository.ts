import { DependencyRepository, CreateDependencyDTO } from '../../domain/interfaces/DependencyRepository';
import { Dependency } from '../../domain/entities/Dependency';

// Forma exacta que devuelve la API (snake_case)
interface DependencyApiResponse {
  requiring_element_id: string;
  required_element_id: string;
}

const toDependency = (raw: DependencyApiResponse): Dependency => ({
  requiringElementId: raw.requiring_element_id,
  requiredElementId: raw.required_element_id,
});

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
    return toDependency(await response.json());
  }
}
