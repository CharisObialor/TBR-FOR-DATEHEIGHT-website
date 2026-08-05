import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

function Preloader({ message, fullPage = false, className }) {
  const content = (
    <div className={cn("flex flex-col items-center justify-center gap-4", className)}>
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-primary/5 animate-ping" />
        <Loader2 className="h-10 w-10 animate-spin text-primary relative" />
      </div>
      {message && (
        <p className="text-sm text-muted-foreground animate-pulse">{message}</p>
      )}
    </div>
  )

  if (fullPage) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
        {content}
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      {content}
    </div>
  )
}

function InlinePreloader({ message, className }) {
  return (
    <div className={cn("flex items-center justify-center py-8", className)}>
      <div className="flex flex-col items-center gap-2">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        {message && (
          <p className="text-sm text-muted-foreground">{message}</p>
        )}
      </div>
    </div>
  )
}

export { Preloader, InlinePreloader }
