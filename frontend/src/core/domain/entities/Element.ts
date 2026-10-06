import { ElementType } from '../enums/ElementType';

export interface Element {
  id: string;
  name: string;
  elementType: ElementType;
  isActive: boolean;
}
