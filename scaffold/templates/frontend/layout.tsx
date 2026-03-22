import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "{{project_name}}",
  description: "{{project_desc}}",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
