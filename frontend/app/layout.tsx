import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Travel AI Planner | Agentic AI Thesis",
  description:
    "AI Travel Planner sử dụng Gemini, FastAPI, Qdrant RAG, LangGraph Agent và Memory System.",
  authors: [
    {
      name: "Phạm Tiến Sơn",
    },
  ],
  icons: {
    icon: "/frontend/public/icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="vi"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}