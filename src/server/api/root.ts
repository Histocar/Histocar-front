import { createCallerFactory, createTRPCRouter } from "~/server/api/trpc";
import { matriculaRouter } from "./routers/matricula";

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  matricula: matriculaRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;

/**
 * Create a server-side caller for the tRPC API.
 * @example
 * const trpc = createCaller(createContext);
 * const res = await trpc.matricula.getLatest();
 *       ^? Matricula | null
 */
export const createCaller = createCallerFactory(appRouter);
