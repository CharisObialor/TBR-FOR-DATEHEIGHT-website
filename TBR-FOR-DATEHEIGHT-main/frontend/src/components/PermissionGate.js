import { useAuth } from '../context/AuthContext';

export default function PermissionGate({ permission, permissions, requireAll = false, children, fallback = null }) {
  const { hasPermission, hasAnyPermission } = useAuth();

  let allowed = false;
  if (permission) {
    allowed = hasPermission(permission);
  } else if (permissions) {
    allowed = requireAll
      ? permissions.every(p => hasPermission(p))
      : hasAnyPermission(permissions);
  } else {
    allowed = true;
  }

  return allowed ? children : fallback;
}

export function useCan(permission) {
  const { hasPermission } = useAuth();
  return hasPermission(permission);
}
