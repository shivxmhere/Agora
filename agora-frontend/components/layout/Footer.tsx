export default function Footer() {
  return (
    <footer className="border-t border-border bg-void py-8 mt-auto">
      <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between font-mono text-xs text-muted">
        <p>© 2026 AGORA Open Marketplace. Built for HackIndia.</p>
        <div className="flex gap-4 mt-4 md:mt-0">
          <a href="#" className="hover:text-cyan">GitHub</a>
          <a href="#" className="hover:text-cyan">Twitter</a>
          <a href="#" className="hover:text-cyan">Discord</a>
        </div>
      </div>
    </footer>
  );
}
