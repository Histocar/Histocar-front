// src/app/_components/Header.tsx
import Link from "next/link";

interface HeaderProps {
  userName?: string;
  isLoggedIn: boolean;
}

export default function Header({ userName, isLoggedIn }: HeaderProps) {
  return (
    <header className="w-full flex items-center justify-between p-4 bg-[#242635]">
      
      <div className="flex items-center">
        {/* <Image src="/logo.png" alt="HistoCar Logo" width={50} height={50} /> */}
        <span className="ml-2 text-2xl font-bold text-white">
          Histo<span className="text-[hsl(280,100%,70%)]">Car</span>
        </span>
      </div>

      {isLoggedIn && (
        <div className="flex items-center space-x-4">
          <span className="text-white">{userName}</span>
          <Link
            href="/api/auth/signout"
            className="rounded-full bg-[#d25efc] px-4 py-2 text-white font-semibold no-underline transition hover:bg-red-700"
          >
            Logout
          </Link>
        </div>
      )}
    </header>
  );
}
