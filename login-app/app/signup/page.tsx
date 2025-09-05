import SignupForm from "@/components/signup-form";

export default function SignUpPage() {
    return (
        <main className="min-h-screen flex items-center justify-center bg-background p-4">
              <div className="w-full max-w-md">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-foreground mb-2">Hello There!</h1>
                  <h1 className="text-3xl font-bold text-foreground mb-2">Welcome to Mental Health Buddy!</h1>
                  <p className="text-muted-foreground">Sign up for a new account!</p>
                </div>
                <SignupForm />
              </div>
            </main>
    )
}