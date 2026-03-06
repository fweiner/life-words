import type { Metadata } from "next";
import "./globals.css";
import { DisableRightClick } from "@/components/shared/DisableRightClick";

export const metadata: Metadata = {
  metadataBase: new URL("https://words.parrotsoftware.com"),
  title: {
    default: "Life Words - Treatment for people with aphasia, brain damage, and memory problems",
    template: "%s | Life Words",
  },
  description: "Accessible treatment applications for people with aphasia, brain damage, and memory problems",
  openGraph: {
    type: "website",
    siteName: "Life Words",
    title: "Life Words - Treatment for people with aphasia, brain damage, and memory problems",
    description: "Accessible treatment applications for people with aphasia, brain damage, and memory problems",
    url: "https://words.parrotsoftware.com",
    images: ["/header.jpg"],
  },
  twitter: {
    card: "summary",
    title: "Life Words - Treatment for people with aphasia, brain damage, and memory problems",
    description: "Accessible treatment applications for people with aphasia, brain damage, and memory problems",
    images: ["/header.jpg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <DisableRightClick />
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
