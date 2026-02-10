import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Containerlab Control Surface',
  description: 'Single-origin FE with server-side gateway translation'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
