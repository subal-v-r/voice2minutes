export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-12">
            <h1 className="text-4xl font-bold text-foreground mb-4">Smart Meeting Minutes Generator</h1>
            <p className="text-xl text-muted-foreground">
              Transform your meeting recordings into structured minutes with AI-powered action tracking
            </p>
          </header>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-lg font-semibold mb-3">Speech-to-Text</h3>
              <p className="text-muted-foreground">
                Convert audio recordings to accurate transcripts with speaker identification
              </p>
            </div>

            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-lg font-semibold mb-3">Smart Summarization</h3>
              <p className="text-muted-foreground">
                Generate structured meeting minutes with agenda items, decisions, and risks
              </p>
            </div>

            <div className="bg-card rounded-lg p-6 border">
              <h3 className="text-lg font-semibold mb-3">Action Tracking</h3>
              <p className="text-muted-foreground">
                Automatically detect and track action items with assignees and deadlines
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <div className="bg-muted rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-4">Ready to Deploy</h2>
              <p className="text-muted-foreground mb-4">
                This is a placeholder page for the Smart Meeting Minutes Generator. The full Python application with
                FastAPI backend is ready for local deployment.
              </p>
              <p className="text-sm text-muted-foreground">
                Refer to the run_instructions.txt file for complete setup and installation guide.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
