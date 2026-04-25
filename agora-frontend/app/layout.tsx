import type { Metadata } from 'next';
import { Space_Mono, JetBrains_Mono, Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { DemoBanner } from '@/components/shared/DemoBanner';

const spaceMono = Space_Mono({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-space-mono',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
});

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-geist-sans',
});

export const metadata: Metadata = {
  title: 'AGORA — The Open AI Agent Marketplace',
  description: 'One hub. Every AI agent. Zero barriers. Discover, deploy and compose autonomous AI agents.',
  keywords: ['AI agents', 'marketplace', 'LangGraph', 'Groq', 'autonomous agents'],
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
        <DemoBanner />
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
