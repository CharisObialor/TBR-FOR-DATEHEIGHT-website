import React, { createContext, useContext, useState, useCallback } from "react"

const PreloaderContext = createContext(null)

export function PreloaderProvider({ children }) {
  const [state, setState] = useState({ visible: false, message: "" })

  const showPreloader = useCallback((message = "") => {
    setState({ visible: true, message })
  }, [])

  const hidePreloader = useCallback(() => {
    setState({ visible: false, message: "" })
  }, [])

  return (
    <PreloaderContext.Provider value={{ ...state, showPreloader, hidePreloader }}>
      {children}
    </PreloaderContext.Provider>
  )
}

export function useGlobalPreloader() {
  const context = useContext(PreloaderContext)
  if (!context) {
    throw new Error("useGlobalPreloader must be used within a PreloaderProvider")
  }
  return context
}

export function usePageLoading(initial = true) {
  const [loading, setLoading] = useState(initial)
  const { showPreloader, hidePreloader } = useGlobalPreloader()

  const startLoading = useCallback((message = "") => {
    setLoading(true)
    showPreloader(message)
  }, [showPreloader])

  const stopLoading = useCallback(() => {
    setLoading(false)
    hidePreloader()
  }, [hidePreloader])

  return { loading, setLoading, startLoading, stopLoading }
}
