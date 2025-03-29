// src/app/_components/Header.tsx
import Link from "next/link";
import { FiUser, FiLogOut, FiClock } from "react-icons/fi";

interface HeaderProps {
  userName?: string;
  isLoggedIn: boolean;
}

export default function Header({ userName, isLoggedIn }: HeaderProps) {
  return (
    <header className="w-full flex items-center justify-between p-4 bg-dark-lighter shadow-md border-b border-gray-800">
      <div className="flex items-center">
        <span className="text-2xl font-bold text-white">
          Histo<span className="text-primary">Car</span>
        </span>
      </div>

      {isLoggedIn ? (
        <div className="flex items-center space-x-4">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-dark-DEFAULT text-light-muted">
            <FiUser className="text-light-muted" />
            <span className="text-light-DEFAULT font-medium">{userName}</span>
          </div>
          <Link
            href="/history"
            className="flex items-center gap-2 rounded-lg bg-dark-lighter hover:bg-dark-DEFAULT px-4 py-2 text-light-muted font-medium no-underline transition"
          >
            <FiClock />
            <span>Mi Historial</span>
          </Link>
          <Link
            href="/api/auth/signout"
            className="flex items-center gap-2 rounded-lg bg-primary hover:bg-primary-hover px-4 py-2 text-white font-medium no-underline transition"
          >
            <FiLogOut />
            <span>Salir</span>
          </Link>
        </div>
      ) : (
        <Link
          href="/api/auth/signin"
          className="flex items-center gap-2 rounded-lg bg-primary hover:bg-primary-hover px-4 py-2 text-white font-medium no-underline transition"
        >
          <FiUser />
          <span>Ingresar</span>
        </Link>
      )}
    </header>
  );
}
