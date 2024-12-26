import { eq } from "drizzle-orm";
import { z } from "zod";
import { env } from "~/env";

import { createTRPCRouter, protectedProcedure, publicProcedure } from "~/server/api/trpc";
import { matriculas } from "~/server/db/schema";

const CARS_API_URL = env.HISTOCAR_CARS_API_URL;

export const matriculaRouter = createTRPCRouter({
  search: publicProcedure
    .input(z.object({ matricula: z.string(), cache: z.boolean().optional() }))
    .mutation(async ({ ctx, input }) => {
      const matricula = input.matricula;
      const cache = input.cache ?? false;

      const userId = ctx.session?.user.id ?? null;

      try {
        if (cache) {
          const matriculaHistorial = await ctx.db.query.matriculas.findFirst({
            where: (matriculas) => eq(matriculas.matricula, matricula),
          });

          if (matriculaHistorial) {
            return {
              matricula: matricula,
              data: matriculaHistorial.data,
              modelo: matriculaHistorial.modelo,
            };
          }
        }

        const response = await fetch(`${CARS_API_URL}/historial?dominio=${matricula}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          console.error("################################################################################");
          console.error({ response });
          console.error("################################################################################");

          throw new Error("Error en la llamada a la API externa");
        }

        const data = await response.json();

        console.log(data);

        const alreadyExists = await ctx.db.query.matriculas.findFirst({
          where: (matriculas) => eq(matriculas.matricula, matricula),
        });

        if (alreadyExists && userId) {
          await ctx.db
            .update(matriculas)
            .set({
              matricula,
              createdById: userId,
              data,
              modelo:
                // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                (data?.PatenteCaba?.["https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos"]?.result?.cabecera
                  ?.tipoModeloFabrica?.descripcion ?? "") as unknown as string,
            })
            .where(eq(matriculas.matricula, matricula));
        } else if (userId) {
          await ctx.db.insert(matriculas).values({
            matricula,
            createdById: userId,
            data,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            modelo: (data?.PatenteCaba?.["https://lb.agip.gob.ar/Empadronados/json/captcha/GetDatos"]?.result?.cabecera
              ?.tipoModeloFabrica?.descripcion ?? "") as unknown as string,
          });
        }

        const carFromDb = await ctx.db.query.matriculas.findFirst({
          where: (matriculas) => eq(matriculas.matricula, matricula),
        });

        return carFromDb;
      } catch (error) {
        console.error(error);
        throw new Error("Error en la llamada a la CarsAPI");
      }
    }),

  getLatest: publicProcedure.query(async ({ ctx }) => {
    try {
      const userId = ctx.session?.user.id ?? null;

      if (!userId) {
        return null;
      }

      const matriculaHistorial = await ctx.db.query.matriculas.findFirst({
        orderBy: (matriculas, { desc }) => [desc(matriculas.createdAt)],
        where: (matriculas) => eq(matriculas.createdById, userId),
      });

      return matriculaHistorial;
    } catch (error) {
      console.error(error);
      throw new Error("Error en la llamada a la CarsAPI");
    }
  }),
});
