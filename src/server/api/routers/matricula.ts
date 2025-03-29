import { desc, eq } from "drizzle-orm";
import { z } from "zod";
import { env } from "~/env";

import { createTRPCRouter, protectedProcedure, publicProcedure } from "~/server/api/trpc";
import { matriculaConsultations, matriculas } from "~/server/db/schema";
import { type DrizzleDB } from "~/server/db/types";
import { type MatriculaRecord } from "~/types/matricula";

const CARS_API_URL = env.HISTOCAR_CARS_API_URL;

// Define utility functions first to avoid circular references
const recordMatriculaConsultation = async (db: DrizzleDB, matriculaId: number, userId: string) => {
  // Check if this user has consulted this matricula before
  const existingConsultation = await db.query.matriculaConsultations.findFirst({
    where: () => 
      eq(matriculaConsultations.matriculaId, matriculaId) &&
      eq(matriculaConsultations.consultedById, userId),
  });
  
  if (existingConsultation) {
    // Update the consultation timestamp
    return await db
      .update(matriculaConsultations)
      .set({ consultedAt: new Date() })
      .where(eq(matriculaConsultations.id, existingConsultation.id));
  } else {
    // Insert new consultation record
    return await db.insert(matriculaConsultations).values({
      matriculaId,
      consultedById: userId
    });
  }
};

// Create a repository layer to handle database operations
const matriculaRepository = {
  /**
   * Find a matricula record by its license plate number
   */
  findByMatricula: async (db: DrizzleDB, matricula: string) => {
    return await db.query.matriculas.findFirst({
      where: () => eq(matriculas.matricula, matricula),
    });
  },
  
  /**
   * Find the latest matricula searched by a user
   */
  findLatestByUserId: async (db: DrizzleDB, userId: string) => {
    // Get the latest consultation by this user
    const latestConsultation = await db.query.matriculaConsultations.findFirst({
      where: () => eq(matriculaConsultations.consultedById, userId),
      orderBy: () => [desc(matriculaConsultations.consultedAt)],
      with: {
        matricula: true
      }
    });
    
    if (latestConsultation?.matricula) {
      return latestConsultation.matricula;
    }
    
    // Fallback to created matriculas if no consultations found
    return await db.query.matriculas.findFirst({
      orderBy: () => [desc(matriculas.createdAt)],
      where: () => eq(matriculas.createdById, userId),
    });
  },
  
  /**
   * Save a matricula record and track the consultation
   */
  saveMatricula: async (db: DrizzleDB, data: MatriculaRecord, userId: string) => {
    const { matricula, createdById, modelo, data: matriculaData } = data;
    
    // Find existing matricula
    const existing = await db.query.matriculas.findFirst({
      where: () => eq(matriculas.matricula, matricula),
    });
    
    let matriculaId: number;
    
    if (existing) {
      // Update existing record only if data has changed
      if (JSON.stringify(existing.data) !== JSON.stringify(matriculaData)) {
        await db
          .update(matriculas)
          .set({ data: matriculaData, modelo })
          .where(eq(matriculas.id, existing.id));
      }
      matriculaId = existing.id;
    } else {
      // Insert new record
      const insertResult = await db.insert(matriculas).values({
        matricula, createdById, data: matriculaData, modelo
      }).returning({ id: matriculas.id });

      if (!insertResult[0]) {
        throw new Error("Error inserting matricula");
      }
      
      matriculaId = insertResult[0].id;
    }
    
    // Record the consultation using the standalone function defined above
    await recordMatriculaConsultation(db, matriculaId, userId);
    
    return matriculaId;
  },
  
  /**
   * Record a consultation of a matricula by a user
   */
  recordConsultation: async (db: DrizzleDB, matriculaId: number, userId: string) => {
    // Use the standalone function to avoid duplication
    return recordMatriculaConsultation(db, matriculaId, userId);
  },
  
  /**
   * Get a matricula with its consultation data
   */
  getMatriculaWithConsultations: async (db: DrizzleDB, matriculaId: number) => {
    const result = await db.query.matriculas.findFirst({
      where: () => eq(matriculas.id, matriculaId),
      with: {
        consultations: {
          with: {
            user: {
              columns: {
                id: true,
                name: true,
                image: true
              }
            }
          },
          orderBy: () => [desc(matriculaConsultations.consultedAt)]
        }
      }
    });
    
    if (result) {
      return {
        ...result,
        consultationCount: result.consultations.length
      };
    }
    
    return null;
  }
};

// Create a service layer to handle business logic
const matriculaService = {
  getModelFromData: (data: Record<string, unknown>): string => {
    try {
      // Extract model information from the data
      const patenteCaba = data?.PatenteCaba as Record<string, unknown> | undefined;
      if (!patenteCaba) return "";
      
      const captchaData = patenteCaba["https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos"] as Record<string, unknown> | undefined;
      if (!captchaData) return "";
      
      const result = captchaData.result as Record<string, unknown> | undefined;
      if (!result) return "";
      
      const cabecera = result.cabecera as Record<string, unknown> | undefined;
      if (!cabecera) return "";
      
      const tipoModeloFabrica = cabecera.tipoModeloFabrica as Record<string, unknown> | undefined;
      if (!tipoModeloFabrica) return "";
      
      return (tipoModeloFabrica.descripcion as string) ?? "";
    } catch (error) {
      console.error("Error extracting model information", error);
      return "";
    }
  },
  
  fetchFromExternalApi: async (matricula: string): Promise<Record<string, unknown>> => {
    const response = await fetch(`${CARS_API_URL}/historial-stream?dominio=${matricula}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("API error:", response.status, response.statusText);
      throw new Error(`Error en la llamada a la API externa: ${response.status}`);
    }

    const data = await response.json();
    return data;
  }
};

// Input validation schema with proper patente formats
const matriculaValidator = z.object({ 
  matricula: z.string()
    .toUpperCase()
    .refine(val => {
      // Validate both old (ABC123) and new (AB123CD) formats
      const oldFormat = /^[A-Z]{3}\d{3}$/;
      const newFormat = /^[A-Z]{2}\d{3}[A-Z]{2}$/;
      return oldFormat.test(val) || newFormat.test(val);
    }, {
      message: "Formato de patente inválido. Debe ser ABC123 o AB123CD"
    }),
  cache: z.boolean().optional().default(false)
});

export const matriculaRouter = createTRPCRouter({
  search: publicProcedure
    .input(matriculaValidator)
    .mutation(async ({ ctx, input }) => {
      const { matricula, cache } = input;
      const userId = ctx.session?.user.id ?? null;

      try {
        // Find existing record
        const existingRecord = await matriculaRepository.findByMatricula(ctx.db, matricula);
        
        // If we have an existing record and cache is requested (or record is fresh - less than 1 day old)
        const recordIsFresh = existingRecord && 
          (new Date().getTime() - new Date(existingRecord.updatedAt ?? existingRecord.createdAt).getTime() < 24 * 60 * 60 * 1000);
        
        if ((cache || recordIsFresh) && existingRecord) {
          // Just record the consultation if user is logged in
          if (userId) {
            // Using the standalone function for better reliability
            await recordMatriculaConsultation(ctx.db, existingRecord.id, userId);
            
            // Return with consultation data
            return await matriculaRepository.getMatriculaWithConsultations(ctx.db, existingRecord.id);
          }
          return existingRecord;
        }

        // Fetch fresh data from external API
        const data = await matriculaService.fetchFromExternalApi(matricula);
        
        // Extract model information
        const modelo = matriculaService.getModelFromData(data);
        
        // If user is logged in, save data and record consultation
        if (userId) {
          // If record exists, we're a consulter, otherwise we're the creator
          const createdById = existingRecord ? existingRecord.createdById : userId;
          
          const matriculaId = await matriculaRepository.saveMatricula(ctx.db, {
            matricula,
            createdById,
            data,
            modelo
          }, userId);
          
          // Return with consultation data
          return await matriculaRepository.getMatriculaWithConsultations(ctx.db, matriculaId);
        }

        // No user, just return the data without saving
        return { matricula, data, modelo };
      } catch (error) {
        console.error("Error in search procedure:", error);
        throw new Error(`Error en la búsqueda: ${error instanceof Error ? error.message : String(error)}`);
      }
    }),

  getLatest: publicProcedure.query(async ({ ctx }) => {
    try {
      const userId = ctx.session?.user.id ?? null;
      if (!userId) {
        return null;
      }

      return await matriculaRepository.findLatestByUserId(ctx.db, userId);
    } catch (error) {
      console.error("Error getting latest:", error);
      throw new Error(`Error obteniendo el último registro: ${error instanceof Error ? error.message : String(error)}`);
    }
  }),
  
  getConsultationHistory: protectedProcedure.query(async ({ ctx }) => {
    try {
      const userId = ctx.session.user.id;
      
      // Get all consultations by this user
      const consultations = await ctx.db.query.matriculaConsultations.findMany({
        where: (c) => eq(c.consultedById, userId),
        orderBy: (c, { desc }) => [desc(c.consultedAt)],
        with: {
          matricula: true
        }
      });
      
      return consultations.map(c => ({
        consulted: c.consultedAt,
        matricula: c.matricula.matricula,
        modelo: c.matricula.modelo,
        id: c.matricula.id
      }));
    } catch (error) {
      console.error("Error getting consultation history:", error);
      throw new Error(`Error obteniendo historial de consultas: ${error instanceof Error ? error.message : String(error)}`);
    }
  })
});
