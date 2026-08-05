import { useTheme } from "next-themes"
import { Toaster as Sonner, toast } from "sonner"

const Toaster = ({
  ...props
}) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme}
      position="bottom-center"
      className="toaster group"
      richColors
      expand={{ duration: 300 }}
      visibleToasts={4}
      gap={8}
      closeButton
      toastOptions={{
        classNames: {
          toast:
            "group toast " +
            "!bg-[#1e293b] !text-white " +
            "!rounded-none !shadow-2xl " +
            "!border-0 " +
            "!px-5 !py-4 " +
            "!min-h-[56px] !min-w-[320px] " +
            "!font-sans !backdrop-blur-md " +
            "!transition-all !duration-200 " +
            "!relative !pr-12 " +
            "hover:!shadow-[0_8px_30px_rgb(0,0,0,0.3)]",
          title:
            "!text-sm !font-semibold !text-white !leading-snug",
          description:
            "!text-[13px] !text-slate-300 !leading-relaxed !mt-0.5",
          actionButton:
            "!bg-white/15 !text-white " +
            "!font-semibold !rounded-lg " +
            "!px-3.5 !py-1.5 " +
            "!text-xs !border !border-white/20 " +
            "!hover:bg-white/25 !transition-colors " +
            "!ml-2",
          cancelButton:
            "!bg-transparent !text-slate-400 " +
            "!font-medium !rounded-lg " +
            "!px-3 !py-1.5 " +
            "!text-xs !border !border-slate-600 " +
            "!hover:bg-white/10 !hover:text-slate-300 " +
            "!transition-colors " +
            "!ml-2",
          closeButton:
            "!absolute !right-0 !top-0 !bottom-0 " +
            "!w-10 " +
            "!flex !items-center !justify-center " +
            "!rounded-none " +
            "!text-slate-500 " +
            "!hover:text-white !hover:bg-white/10 " +
            "!transition-all !duration-150 " +
            "!cursor-pointer " +
            "!border-0 !border-l !border-l-white/10 " +
            "!bg-transparent " +
            "!p-0 !m-0",
        },
      }}
      icons={{
        success: (
          <div className="!w-6 !h-6 !rounded-full !bg-emerald-500/20 !flex !items-center !justify-center !shrink-0">
            <svg className="!w-3.5 !h-3.5 !text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        ),
        error: (
          <div className="!w-6 !h-6 !rounded-full !bg-red-500/20 !flex !items-center !justify-center !shrink-0">
            <svg className="!w-3.5 !h-3.5 !text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        ),
        warning: (
          <div className="!w-6 !h-6 !rounded-full !bg-amber-500/20 !flex !items-center !justify-center !shrink-0">
            <svg className="!w-3.5 !h-3.5 !text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m0-3.75h.008v.008H12V9z" />
            </svg>
          </div>
        ),
        info: (
          <div className="!w-6 !h-6 !rounded-full !bg-blue-500/20 !flex !items-center !justify-center !shrink-0">
            <svg className="!w-3.5 !h-3.5 !text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
          </div>
        ),
      }}
      {...props}
    />
  )
}

export { Toaster, toast }
