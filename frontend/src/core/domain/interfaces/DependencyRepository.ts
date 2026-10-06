import { Dependency } from '../entities/Dependency';

export interface CreateDependencyDTO {
  requiring_element_id: string;
  required_element_id: string;
}

export interface DependencyRepository {
  register(dependency: CreateDependencyDTO): Promise<Dependency>;
}
