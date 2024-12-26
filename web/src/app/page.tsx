// src/app/page.tsx
import { LatestMatricula } from "~/app/_components/post";
import { getServerAuthSession } from "~/server/auth";
import { HydrateClient } from "~/trpc/server";
import Header from "~/app/_components/header"; // Importa el Header

export default async function Home() {
  const session = await getServerAuthSession();

  return (
    <HydrateClient>
      <Header userName={session?.user?.name ?? undefined} isLoggedIn={!!session} />
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white">
        <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
            ¡Toda la historia de tu próximo usado, al alcance de un <span className="text-[#cb4fff]">HistoCar!</span>
          </h1>
          <div className="flex flex-col items-center gap-2">
            <div className="flex flex-col items-center justify-center gap-4"></div>
          </div>

          {session?.user && <LatestMatricula />}
        </div>
      </main>
    </HydrateClient>
  );
}
