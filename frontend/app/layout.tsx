import type { Metadata } from "next";
import { Inter, Geist } from "next/font/google";
import { Providers } from "@/components/providers";
import "./globals.css";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MemoryChat",
  description: "AI-native messaging with long-term relationship memory",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className={`${inter.variable} font-sans antialiased text-slate-900 h-screen overflow-hidden`} suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
