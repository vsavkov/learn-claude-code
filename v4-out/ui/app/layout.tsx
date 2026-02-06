import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Containerlab Console',
  description: 'Web UI for containerlab API gateway via BFF'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
