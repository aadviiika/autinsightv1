import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AutInsight | A caregiver guide',
  description: 'A research prototype to help caregivers organize developmental observations and plan a conversation with a professional.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><header className="site-header"><a className="brand" href="/" aria-label="AutInsight home"><span className="brand-mark" aria-hidden="true">a</span><span>AutInsight</span></a><a className="header-cta" href="/screening">Start the caregiver guide <span aria-hidden="true">→</span></a></header>{children}<footer className="site-footer"><span>AutInsight · Final-year research prototype</span><span>Informational only · Not a diagnosis</span></footer></body></html>;
}
