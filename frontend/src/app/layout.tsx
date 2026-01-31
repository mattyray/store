import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ChatWidget } from "@/components/chat";
import { CartProvider } from "@/contexts/CartContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export const metadata: Metadata = {
  title: "Matthew Raynor Photography | Fine Art Prints of the Hamptons",
  description: "Museum-quality fine art photography prints of the Hamptons. Limited edition aluminum and archival paper prints.",
  keywords: ["Hamptons photography", "fine art prints", "beach photography", "landscape photography", "Matthew Raynor"],
  openGraph: {
    title: "Matthew Raynor Photography",
    description: "Museum-quality fine art photography prints of the Hamptons. Limited edition aluminum and archival paper prints.",
    url: "https://store.matthewraynor.com",
    siteName: "Matthew Raynor Photography",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Matthew Raynor Photography",
    description: "Museum-quality fine art photography prints of the Hamptons.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-white text-gray-900`}>
        <CartProvider>
          <Header />
          <main className="min-h-screen">
            {children}
          </main>
          <Footer />
          <ChatWidget />
        </CartProvider>
      </body>
    </html>
  );
}
