import { DependencyRepository, CreateDependencyDTO } from '../../domain/interfaces/DependencyRepository';
import { Dependency } from '../../domain/entities/Dependency';
import { Element } from '../../domain/entities/Element';
import { ElementType } from '../../domain/enums/ElementType';

export class RegisterDependencyUseCase {
  constructor(private dependencyRepository: DependencyRepository) {}

  async execute(requiringElement: Element, requiredElement: Element): Promise<Dependency> {
    // 1. Validaciones puras de negocio en el frontend (Fail Fast)
    const reqType = requiringElement.elementType;
    const requiredType = requiredElement.elementType;

    if (reqType === ElementType.PROVEEDOR) {
      throw new Error('Un proveedor no puede depender de ningún elemento.');
    }

    if (reqType === ElementType.INSUMO && requiredType !== ElementType.PROVEEDOR) {
      throw new Error('Un insumo solo puede depender de un proveedor.');
    }

    if (reqType === ElementType.PRODUCTO && requiredType === ElementType.PROVEEDOR) {
      throw new Error('Un producto no puede depender directamente de un proveedor.');
    }

    // 2. Si es válido, ejecutar la llamada al puerto (infraestructura)
    const dto: CreateDependencyDTO = {
      requiring_element_id: requiringElement.id,
      required_element_id: requiredElement.id,
    };

    return await this.dependencyRepository.register(dto);
  }
}
