"use client";

import { useState } from "react";
import ReactJson from "react-json-view";
import { api } from "~/trpc/react";
import { FiSearch } from "react-icons/fi"; // Importa el icono de lupa

export function LatestMatricula() {
  const utils = api.useUtils();
  const [matricula, setMatricula] = useState("");
  const [cache, setCache] = useState(false);

  const buscarMatricula = api.matricula.search.useMutation({
    onSuccess: async () => {
      await utils.matricula.getLatest.invalidate();
      setMatricula("");
    },
    onError: (error) => {
      console.error(error);
      setMatricula("");
    },
  });

  return (
    <div className="w-full flex flex-col items-center">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          buscarMatricula.mutate({ matricula, cache });
        }}
        className="flex flex-col gap-2 w-full max-w-3xl mx-4"
      >
      <div className="flex items-center w-full max-w-2xl mx-auto">
        <input
          type="text"
          placeholder="Matricula"
          value={matricula}
          onChange={(e) => setMatricula(e.target.value)}
          className="flex-grow rounded-full px-6 py-4 text-black w-full h-12 text-base md:text-lg lg:text-xl"
        />
        <button
          type="submit"
          className="ml-2 p-3 bg-white/10 rounded-full transition hover:bg-white/20 flex items-center justify-center h-12 w-12 text-base md:text-lg lg:text-xl"
          disabled={buscarMatricula.isPending}
        >
          <FiSearch size={20} />
        </button>
      </div>
        <div className="hidden">
          <label htmlFor="">
            <span>Cache activado</span>
            <input
              type="checkbox"
              checked={cache}
              onChange={(e) => setCache(e.target.checked)}
              className="rounded-full bg-white/10 px-4 py-2 text-black transition hover:bg-white/20"
            />
          </label>
        </div>
      </form>

      <div className="mt-4 w-full max-w-3xl mx-4">
        {buscarMatricula.isPending && <p>Buscando matricula...</p>}
        {buscarMatricula.isError && <p>Error al buscar matricula</p>}
        {buscarMatricula.isSuccess && (
          <div>
            <p>Matricula: {buscarMatricula.data?.matricula ?? ""}</p>
            <p>Modelo: {buscarMatricula.data?.modelo ?? ""}</p>
          </div>
        )}

        {buscarMatricula.isSuccess && (
          <div className="w-full bg-zinc-500 p-4 rounded-lg">
            <ReactJson src={buscarMatricula.data?.data ?? {}} theme={"tomorrow"} />
          </div>
        )}
      </div>
    </div>
  );
}
