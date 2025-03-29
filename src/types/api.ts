/**
 * Types for API responses
 */

export interface User {
  id: string;
  name?: string;
  image?: string;
}

export interface MatriculaConsultation {
  id: number;
  matriculaId: number;
  consultedById: string;
  consultedAt: string;
  user?: User;
}

export interface MatriculaWithConsultations {
  id: number;
  matricula: string;
  modelo: string;
  data: Record<string, unknown>;
  createdById: string;
  createdAt: string;
  updatedAt?: string;
  consultations: MatriculaConsultation[];
  consultationCount: number;
}