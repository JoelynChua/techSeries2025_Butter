import LoginForm from "@/components/login-form"

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Welcome Back to Mental Health Buddy</h1>
          <p className="text-muted-foreground">Sign in to your account</p>
        </div>
        <LoginForm />
      </div>
    </main>
  )
}
