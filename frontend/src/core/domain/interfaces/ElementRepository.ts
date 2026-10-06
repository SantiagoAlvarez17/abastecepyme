import { Element } from '../entities/Element';
import { ElementType } from '../enums/ElementType';

export interface CreateElementDTO {
  name: string;
  element_type: ElementType;
}

export interface ElementRepository {
  getAll(): Promise<Element[]>;
  create(element: CreateElementDTO): Promise<Element>;
}
