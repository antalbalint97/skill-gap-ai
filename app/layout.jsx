import "./globals.css";

export const metadata = {
  title: "Skill Gap Radar Agent",
  description: "Enterprise workforce intelligence dashboard for skill extraction, market comparison, gap detection, and recommendations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
