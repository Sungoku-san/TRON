import "./globals.css"

export const metadata = {
  title: "TRON v2",
  description: "Voice + Text AI Assistant",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
