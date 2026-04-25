import type { Metadata } from 'next';
import { Space_Mono, JetBrains_Mono } from 'next/font/google';
import localFont from 'next/font/local';
import './globals.css';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

const spaceMono = Space_Mono({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-space-mono',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
});

// We can just use standard sans-serif for Geist if we don't have the local file downloaded, 
// but using standard next/font/google for Inter as a fallback if Geist isn't configured 
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], variable: '--font-geist-sans' });

export const metadata: Metadata = {
  title: 'AGORA — The Open AI Agent Marketplace',
  description: 'One hub. Every AI agent. Zero barriers.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${spaceMono.variable} ${jetbrainsMono.variable} ${inter.variable} min-h-screen flex flex-col bg-void text-primary font-body antialiased`}
      >
        <div className="bg-lime text-void text-center py-1 font-mono text-xs font-bold w-full uppercase tracking-widest z-[100] relative">
          ⚠️ Running on Demo Data — Groq + Tavily APIs active for HackIndia evaluation ⚠️
        </div>
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
