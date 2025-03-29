import type { PostgresJsDatabase } from 'drizzle-orm/postgres-js';
import type * as schema from './schema';

/**
 * Properly typed database type to be used throughout the application
 */
export type DrizzleDB = PostgresJsDatabase<typeof schema>;