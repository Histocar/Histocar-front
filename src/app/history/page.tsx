// src/app/history/page.tsx
import { redirect } from "next/navigation";
import Link from "next/link";
import { FiChevronLeft, FiClock, FiUser } from "react-icons/fi";
import { getServerAuthSession } from "~/server/auth";
import { HydrateClient } from "~/trpc/server";
import Header from "~/app/_components/header";
import { api } from "~/trpc/server";

export default async function ConsultationHistoryPage() {
  // Check if user is authenticated
  const session = await getServerAuthSession();
  if (!session) {
    redirect("/api/auth/signin");
  }

  // Fetch consultation history
  const consultations = await api.matricula.getConsultationHistory();

  return (
    <HydrateClient>
      <Header userName={session.user.name ?? undefined} isLoggedIn={true} />
      <main className="flex min-h-screen flex-col bg-dark-DEFAULT text-light-DEFAULT">
        <div className="container mx-auto px-4 py-16">
          <div className="mb-6">
            <Link 
              href="/"
              className="inline-flex items-center gap-1 text-primary hover:text-primary-hover transition-colors"
            >
              <FiChevronLeft />
              <span>Volver a la búsqueda</span>
            </Link>
          </div>
          
          <h1 className="text-2xl font-bold mb-8">Mi historial de consultas</h1>
          
          {consultations.length === 0 ? (
            <div className="p-6 rounded-lg text-center border border-gray-700">
              <p className="text-light-DEFAULT">No has realizado ninguna consulta todavía.</p>
              <Link 
                href="/"
                className="mt-4 inline-block px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
              >
                Buscar una patente
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {consultations.map((consultation) => (
                <Link 
                  href={`/?matricula=${consultation.matricula}`}
                  key={String(consultation.id)}
                  className="p-4 rounded-lg border border-gray-700 hover:border-primary transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="bg-primary/10 text-primary px-2 py-1 rounded-md text-sm font-medium">
                      {consultation.matricula}
                    </span>
                    <div className="flex items-center text-light-muted text-xs">
                      <FiClock className="mr-1" />
                      {new Date(consultation.consulted).toLocaleDateString()}
                    </div>
                  </div>
                  
                  <h3 className="font-semibold text-lg mb-1 text-light-DEFAULT">
                    {consultation.modelo || "Vehículo"}
                  </h3>
                  
                  <div className="mt-3 pt-2 border-t border-gray-700 flex justify-between items-center">
                    <div className="flex items-center text-light-muted text-xs">
                      <FiUser className="mr-1" />
                      Consultado por ti
                    </div>
                    <span className="text-primary text-sm">Ver detalles →</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </HydrateClient>
  );
}