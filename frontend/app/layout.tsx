import type { Metadata } from "next";
import "./globals.css";
import { DisableRightClick } from "@/components/shared/DisableRightClick";

export const metadata: Metadata = {
  title: "Life Words - Treatment for people with aphasia, brain damage, and memory problems",
  description: "Accessible treatment applications for people with aphasia, brain damage, and memory problems",
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
