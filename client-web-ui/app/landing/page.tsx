import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Cloud, 
  Zap, 
  Shield, 
  Users, 
  ArrowRight,
  Cpu,
  Database,
  Globe
} from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6">
            Distributed Compute
            <span className="text-primary"> Made Simple</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Share and utilize computational resources across a decentralized network. 
            Run your Python tasks on idle computers worldwide.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Why Choose Cloudless?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A peer-to-peer platform that connects compute providers with task submitters
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
                    <Card className="border border-border shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Cpu className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Distributed Computing</CardTitle>
              <CardDescription>
                Tap into idle computational resources across the globe
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-center">
                Submit Python tasks and let our network of providers execute them efficiently.
              </p>
            </CardContent>
          </Card>

          <Card className="border border-border shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-green-500" />
              </div>
              <CardTitle>Secure & Private</CardTitle>
              <CardDescription>
                Your data and computations are protected
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-center">
                Tasks run in isolated Docker containers with encrypted communication.
              </p>
            </CardContent>
          </Card>

          <Card className="border border-border shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-purple-500" />
              </div>
              <CardTitle>Community Driven</CardTitle>
              <CardDescription>
                Earn credits by sharing resources
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-center">
                Contribute your idle CPU and RAM to earn credits for future computations.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-20 bg-muted/50">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            How It Works
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Simple steps to get started with distributed computing
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-foreground">Submit Task</h3>
              <p className="text-muted-foreground">
                Upload your Python script and specify resource requirements
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-green-500">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-foreground">Distribute</h3>
              <p className="text-muted-foreground">
                Our system finds available providers and distributes your task
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-purple-500">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-foreground">Get Results</h3>
              <p className="text-muted-foreground">
                Monitor progress and download results when complete
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
            Ready to Start Computing?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join the distributed computing revolution. Submit your first task today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="text-lg px-8 py-6">
                Create Account
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; 2024 Cloudless. Distributed Compute Sharing Platform.</p>
        </div>
      </footer>
    </div>
  )
}
