"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import ReactJson from "react-json-view";
import { api } from "~/trpc/react";
import { FiSearch, FiInfo } from "react-icons/fi";
import type { MatriculaWithConsultations } from "~/types/api";

export function LatestMatricula() {
  const searchParams = useSearchParams();
  const initialMatricula = searchParams.get("matricula") ?? "";
  
  const utils = api.useUtils();
  const [matricula, setMatricula] = useState(initialMatricula);
  const [cache, setCache] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const buscarMatricula = api.matricula.search.useMutation({
    onSuccess: async () => {
      await utils.matricula.getLatest.invalidate();
    },
    onError: (error) => {
      console.error(error);
    },
  });
  
  // Auto-search when coming from history page with a matricula parameter
  useEffect(() => {
    if (initialMatricula && validateMatricula(initialMatricula.toUpperCase())) {
      buscarMatricula.mutate({ matricula: initialMatricula.toUpperCase(), cache: true });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialMatricula]);

  // Format validation for patente/matricula
  const validateMatricula = (value: string) => {
    // Accept both old (ABC123) and new (AB123CD) format
    const oldFormat = /^[A-Z]{3}\d{3}$/;
    const newFormat = /^[A-Z]{2}\d{3}[A-Z]{2}$/;
    return oldFormat.test(value) || newFormat.test(value);
  };

  const isValidFormat = matricula.length > 0 ? validateMatricula(matricula.toUpperCase()) : true;

  return (
    <div className="w-full flex flex-col items-center">
      <div className="p-6 rounded-lg shadow-lg w-full max-w-3xl mx-4 border border-gray-800 bg-dark-card text-light-muted">
        <h2 className="text-xl font-bold mb-4 text-light-DEFAULT">Consulta de Historial Vehicular</h2>
        
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (isValidFormat) {
              buscarMatricula.mutate({ matricula: matricula.toUpperCase(), cache });
            }
          }}
          className="flex flex-col gap-4 w-full"
        >
          <div className="space-y-2 ">
            <label className="block text-sm font-medium">
              Patente / Matrícula <span className="text-red-500">*</span>
            </label>
            
            <div className="flex items-center w-full">
              <div className="relative flex-grow">
                <input
                  type="text"
                  placeholder="Ingrese la patente (ej: ABC123 o AB123CD)"
                  value={matricula}
                  onChange={(e) => setMatricula(e.target.value.toUpperCase())}
                  className={`w-full rounded-l-lg px-6 py-4 text-black h-12 text-base border-2 focus:outline-none focus:ring-2 ${
                    !isValidFormat && matricula.length > 0
                      ? "border-red-500 focus:ring-red-500"
                      : "border-gray-300 focus:ring-primary"
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowHelp(!showHelp)}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  <FiInfo size={16} />
                </button>
              </div>
              <button
                type="submit"
                className="ml-0 p-3 bg-primary hover:bg-primary-hover rounded-r-lg transition text-white flex items-center justify-center h-12 px-6"
                disabled={buscarMatricula.isPending || !isValidFormat}
              >
                <FiSearch size={20} className="mr-2" />
                <span>Buscar</span>
              </button>
            </div>

            {!isValidFormat && matricula.length > 0 && (
              <p className="text-red-500 text-sm mt-1">
                Formato de patente inválido. Use ABC123 o AB123CD.
              </p>
            )}

            {showHelp && (
              <div className="mt-2 p-3 bg-dark-lighter rounded-md text-sm">
                <p className="font-medium mb-1">Formatos de patente válidos:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li><span className="font-mono bg-black/30 px-1 rounded">ABC123</span> - Formato anterior (3 letras, 3 números)</li>
                  <li><span className="font-mono bg-black/30 px-1 rounded">AB123CD</span> - Formato actual (2 letras, 3 números, 2 letras)</li>
                </ul>
              </div>
            )}
          </div>

          <div className="hidden">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={cache}
                onChange={(e) => setCache(e.target.checked)}
                className="h-4 w-4"
              />
              <span>Usar caché</span>
            </label>
          </div>
        </form>
      </div>

      <div className="mt-6 w-full max-w-3xl mx-4">
        {buscarMatricula.isPending && (
          <div className="p-4 rounded-lg text-center border border-gray-800 bg-dark-card text-light-muted">
            <p className="text-light-DEFAULT">Buscando información de la patente {matricula}...</p>
          </div>
        )}
        
        {buscarMatricula.isError && (
          <div className="bg-red-900/30 p-4 rounded-lg border border-red-800">
            <p className="text-red-200">Error al buscar la patente. Por favor, intenta nuevamente.</p>
          </div>
        )}
        
        {buscarMatricula.isSuccess && (
          <div className="space-y-4">
            <div className="p-4 rounded-lg border border-gray-700 bg-dark-card text-light-muted">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-light-muted text-sm">Patente</p>
                  <p className="font-medium text-light-DEFAULT">{(buscarMatricula.data as MatriculaWithConsultations)?.matricula ?? ""}</p>
                </div>
                <div>
                  <p className="text-light-muted text-sm">Modelo</p>
                  <p className="font-medium text-light-DEFAULT">{(buscarMatricula.data as MatriculaWithConsultations)?.modelo ?? "No disponible"}</p>
                </div>
              </div>
              
              {/* Consultation statistics */}
              {(buscarMatricula.data as MatriculaWithConsultations)?.consultationCount && (buscarMatricula.data as MatriculaWithConsultations).consultationCount > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-700">
                  <div className="flex justify-between items-center">
                    <p className="text-light-muted text-sm">Consultas totales</p>
                    <span className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs font-semibold">
                      {(buscarMatricula.data as MatriculaWithConsultations)?.consultationCount ?? 0}
                    </span>
                  </div>
                  
                  {/* Display recent consultations if any exist */}
                  {(buscarMatricula.data as MatriculaWithConsultations)?.consultations && (buscarMatricula.data as MatriculaWithConsultations).consultations.length > 0 && (
                    <div className="mt-2">
                      <p className="text-light-muted text-sm mb-2">Consultado por</p>
                      <div className="flex flex-wrap gap-2">
                        {(buscarMatricula.data as MatriculaWithConsultations).consultations.slice(0, 5).map((consultation) => (
                          <div 
                            key={consultation.id} 
                            className="flex items-center gap-1 px-2 py-1 bg-dark-lighter rounded-md text-xs border-gray-700 border"
                            title={`Consultado ${new Date(consultation.consultedAt).toLocaleString()}`}
                          >
                            {consultation.user?.name ?? "Usuario"}
                          </div>
                        ))}
                        
                        {(buscarMatricula.data as MatriculaWithConsultations).consultations.length > 5 && (
                          <div className="px-2 py-1 bg-dark-lighter rounded-md text-xs">
                            +{(buscarMatricula.data as MatriculaWithConsultations).consultations.length - 5} más
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="bg-dark-card text-light-muted p-4 rounded-lg border border-gray-700">
              <h3 className="text-lg font-semibold mb-3">Datos completos</h3>
              <ReactJson 
                src={(buscarMatricula.data as MatriculaWithConsultations)?.data ?? {}} 
                theme="monokai" 
                displayDataTypes={false}
                displayObjectSize={false}
                collapsed={1}
                style={{ backgroundColor: "transparent" }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
