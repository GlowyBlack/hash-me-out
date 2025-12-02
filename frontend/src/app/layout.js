// src/app/layout.js
import "./globals.css";

export const metadata = {
  title: "Hash Me Out",
  description: "Book Review App",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        {/* If you want light or dark preference, it must be a meta tag here */}
        <meta name="color-scheme" content="light only" />
      </head>

      <body className="antialiased">
        {/* Force consistent light color scheme across macOS and Windows */}
      <body className="">
          <meta name="color-scheme" content="dark only" />
        {children}
      </body>
    </html>
  );
}
