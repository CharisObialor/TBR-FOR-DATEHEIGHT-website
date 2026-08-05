const CART_KEY = 'tbr_service_cart';
const MAX_ITEMS = 10;

export function getCart() {
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function addToCart(service, monthsAhead = 1) {
  const cart = getCart();
  if (cart.some(item => item.serviceId === service.id)) return cart;
  if (cart.length >= MAX_ITEMS) return cart;
  const updated = [...cart, {
    serviceId: service.id,
    slug: service.slug,
    title: service.title,
    description: service.description || '',
    priceRange: service.price_range || '',
    category: service.category || '',
    notes: '',
    isRecurring: service.is_recurring || false,
    billingCycle: service.billing_cycle || '',
    basePricePerCycle: service.base_price_per_cycle || 0,
    monthsAhead: service.is_recurring ? monthsAhead : 1,
  }];
  localStorage.setItem(CART_KEY, JSON.stringify(updated));
  return updated;
}

export function removeFromCart(serviceId) {
  const updated = getCart().filter(item => item.serviceId !== serviceId);
  localStorage.setItem(CART_KEY, JSON.stringify(updated));
  return updated;
}

export function updateCartItemNotes(serviceId, notes) {
  const updated = getCart().map(item =>
    item.serviceId === serviceId ? { ...item, notes } : item
  );
  localStorage.setItem(CART_KEY, JSON.stringify(updated));
  return updated;
}

export function updateCartItemMonths(serviceId, monthsAhead) {
  const updated = getCart().map(item =>
    item.serviceId === serviceId ? { ...item, monthsAhead } : item
  );
  localStorage.setItem(CART_KEY, JSON.stringify(updated));
  return updated;
}

export function clearCart() {
  localStorage.removeItem(CART_KEY);
}

export function isInCart(serviceId) {
  return getCart().some(item => item.serviceId === serviceId);
}

export function getCartCount() {
  return getCart().length;
}

// ── Pending uploads (for pre-order document uploads) ──────────────────────
const UPLOADS_KEY = 'tbr_pending_uploads';

export function getPendingUploads() {
  try {
    const raw = localStorage.getItem(UPLOADS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function addPendingUpload(serviceId, docName, fileData) {
  const all = getPendingUploads();
  if (!all[serviceId]) all[serviceId] = {};
  all[serviceId][docName] = fileData;
  localStorage.setItem(UPLOADS_KEY, JSON.stringify(all));
  return all;
}

export function getPendingUploadsForService(serviceId) {
  return getPendingUploads()[serviceId] || {};
}

export function clearPendingUploads() {
  localStorage.removeItem(UPLOADS_KEY);
}
