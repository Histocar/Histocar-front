/**
 * Types related to vehicle matricula (license plate) data
 */

/**
 * Represents a vehicle matricula record in the database
 */
export interface MatriculaRecord {
  /** The vehicle license plate number */
  matricula: string;
  
  /** The user ID who created this record */
  createdById: string;
  
  /** The vehicle model name */
  modelo: string;
  
  /** The complete vehicle data from various sources */
  data: Record<string, unknown>;
}

/**
 * Input for searching a matricula
 */
export interface MatriculaSearchInput {
  /** The vehicle license plate to search for */
  matricula: string;
  
  /** Whether to use cached data if available */
  cache?: boolean;
}

/**
 * Represents a consultation record in the database
 */
export interface MatriculaConsultationRecord {
  /** The ID of the matricula that was consulted */
  matriculaId: number;
  
  /** The user ID who consulted this record */
  consultedById: string;
  
  /** When the consultation occurred */
  consultedAt: Date;
}

/**
 * Represents a matricula with consultation data
 */
export interface MatriculaWithConsultations extends MatriculaRecord {
  /** The users who have consulted this matricula */
  consultations?: MatriculaConsultationRecord[];
  
  /** Total number of consultations */
  consultationCount?: number;
}

/**
 * Vehicle patente format types
 */
export enum PatenteFormat {
  /** Old format: ABC123 */
  OLD = "old",
  
  /** New format: AB123CD */
  NEW = "new"
}