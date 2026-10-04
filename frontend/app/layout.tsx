import type { Metadata, Viewport } from "next";
import { Outfit, Inter, JetBrains_Mono } from "next/font/google";
import { Background } from "@/components/ui";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#07070d",
};

export const metadata: Metadata = {
  title: "Faceometry — The Geometry Behind Your Face",
  description:
    "Analyze your facial proportions, symmetry, and classical geometric ratios using computer vision and mathematics. AI-powered facial geometry and symmetry analysis.",
  keywords: [
    "facial geometry",
    "face analysis",
    "symmetry",
    "golden ratio",
    "computer vision",
    "facial proportions",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-scroll-behavior="smooth" className={`${outfit.variable} ${inter.variable} ${jetbrains.variable}`}>
      <body>
        <Background />
        {children}
      </body>
    </html>
  );
}
