import { MobileNav } from "./MobileNav";
import { Sidebar } from "./Sidebar";

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen md:flex">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <MobileNav />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-8 sm:py-10">
          {children}
        </main>
      </div>
    </div>
  );
}