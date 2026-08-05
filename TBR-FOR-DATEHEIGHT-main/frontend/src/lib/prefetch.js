const prefetchedChunks = new Set()
const prefetchedApi = new Set()
let idleCallbackId = null

export function prefetchRoute(factory) {
  if (typeof factory !== 'function') return
  const key = factory.toString()
  if (prefetchedChunks.has(key)) return
  prefetchedChunks.add(key)
  factory()
}

export function prefetchApi(url, params = null) {
  const key = params ? `${url}?${JSON.stringify(params)}` : url
  if (prefetchedApi.has(key)) return
  prefetchedApi.add(key)
  import('../lib/api').then(({ default: api }) => {
    api.get(url, { params }).catch(() => {})
  })
}

const routeFactories = {}

export function registerRouteFactory(path, factory) {
  routeFactories[path] = factory
}

export function prefetchRouteByPath(path) {
  if (routeFactories[path]) prefetchRoute(routeFactories[path])
}

export function prefetchOnInteraction(ref, path) {
  if (!ref || !path) return
  const handler = () => prefetchRouteByPath(path)
  ref.addEventListener('mouseenter', handler, { once: true })
  ref.addEventListener('focus', handler, { once: true })
}

export function prefetchOnIdle(factories) {
  if (typeof requestIdleCallback === 'undefined') return
  if (idleCallbackId) cancelIdleCallback(idleCallbackId)
  idleCallbackId = requestIdleCallback(() => {
    factories.forEach(f => prefetchRoute(f))
  }, { timeout: 2000 })
}
