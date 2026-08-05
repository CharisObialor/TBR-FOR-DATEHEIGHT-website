import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCart } from '../lib/cart';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog';
import LayoutDashboard from 'lucide-react/dist/esm/icons/layout-dashboard';
import Package from 'lucide-react/dist/esm/icons/package';
import Upload from 'lucide-react/dist/esm/icons/upload';
import CreditCard from 'lucide-react/dist/esm/icons/credit-card';
import Wallet from 'lucide-react/dist/esm/icons/wallet';
import LogOut from 'lucide-react/dist/esm/icons/log-out';
import MenuIcon from 'lucide-react/dist/esm/icons/menu';
import XIcon from 'lucide-react/dist/esm/icons/x';
import LifeBuoy from 'lucide-react/dist/esm/icons/life-buoy';
import Shield from 'lucide-react/dist/esm/icons/shield';
import Ticket from 'lucide-react/dist/esm/icons/ticket';
import Briefcase from 'lucide-react/dist/esm/icons/briefcase';
import ClipboardCheck from 'lucide-react/dist/esm/icons/clipboard-check';
import Receipt from 'lucide-react/dist/esm/icons/receipt';
import History from 'lucide-react/dist/esm/icons/history';
import ListChecks from 'lucide-react/dist/esm/icons/list-checks';
import Cog from 'lucide-react/dist/esm/icons/cog';
import Users from 'lucide-react/dist/esm/icons/users';
import GitPullRequest from 'lucide-react/dist/esm/icons/git-pull-request';
import AlertTriangle from 'lucide-react/dist/esm/icons/alert-triangle';
import Clock from 'lucide-react/dist/esm/icons/clock';
import Building from 'lucide-react/dist/esm/icons/building-2';
import UserPlus from 'lucide-react/dist/esm/icons/user-plus';
import RefreshCw from 'lucide-react/dist/esm/icons/refresh-cw';
import Copy from 'lucide-react/dist/esm/icons/copy';
import { toast } from 'sonner';
import { orderDocsAPI, adminAPI, workflowAPI, orgAPI, prefetch } from '../lib/api';

// Prefetch map: page path → API calls to warm on hover
const PREFETCH_MAP = {
  '/portal/admin/dashboard': () => Promise.all([
    prefetch('/admin/stats'),
    prefetch('/admin/orders', { mine: true }),
    prefetch('/admin/deadlines', { days: 7 }),
  ]),
  '/portal/admin/my-tasks': () => Promise.all([
    prefetch('/admin/orders', { mine: true }),
    prefetch('/admin/deadlines', { days: 14 }),
    prefetch('/admin/tickets', { mine: true }),
  ]),
  '/portal/admin/team-tasks': () => prefetch('/workflow/team-tasks'),
  '/portal/admin/jobs': () => Promise.all([
    prefetch('/admin/orders', { mine: false }),
    prefetch('/admin/users'),
  ]),
  '/portal/admin/users': () => prefetch('/admin/users'),
  '/portal/admin/clients': () => prefetch('/admin/orders'),
  '/portal/admin/workflow': () => Promise.all([
    prefetch('/workflow/queue'),
    prefetch('/workflow/overview'),
  ]),
  '/portal/admin/review': () => prefetch('/workflow/review-queue'),
  '/portal/admin/escalations': () => prefetch('/workflow/escalations'),
  '/portal/dashboard': () => Promise.all([
    prefetch('/dashboard/stats'),
    prefetch('/services'),
  ]),
};

const PortalSidebar = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [cartCount, setCartCount] = useState(0);
  const { user, logout, hasRole, hasPermission, fetchUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Organization state
  const [org, setOrg] = useState(null);
  const [orgLoading, setOrgLoading] = useState(true);
  const [joinCode, setJoinCode] = useState('');
  const [joinLoading, setJoinLoading] = useState(false);
  const [memberEmail, setMemberEmail] = useState('');
  const [addMemberLoading, setAddMemberLoading] = useState(false);
  const [orgCode, setOrgCode] = useState('');
  const [codeLoading, setCodeLoading] = useState(false);
  const [showOrgSection, setShowOrgSection] = useState(false);
  const [members, setMembers] = useState([]);
  const [showMembers, setShowMembers] = useState(false);
  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false);

  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [sidebarOpen]);

  // Update cart count on navigation
  useEffect(() => {
    setCartCount(getCart().length);
  }, [location.pathname]);

  useEffect(() => {
    const fetchCount = () => {
      orderDocsAPI.listAdminOrders(true).then(res => {
        const orders = res.data.orders || res.data || [];
        setPendingCount(orders.filter(o => !['completed', 'cancelled', 'approved'].includes(o.status)).length);
      }).catch(() => {});
    };
    if (!hasRole('client')) {
      fetchCount();
      const interval = setInterval(fetchCount, 60000);
      return () => clearInterval(interval);
    }
  }, [hasRole]);

  const handleNavHover = useCallback((path) => {
    const prefecther = PREFETCH_MAP[path];
    if (prefecther) prefecther();
  }, []);

  useEffect(() => {
    orgAPI.getMyOrg().then(res => {
      if (res.data.org) {
        setOrg(res.data.org);
      }
    }).catch(() => {}).finally(() => setOrgLoading(false));
  }, [user]);

  const handleJoinOrg = async () => {
    if (!joinCode.trim()) return;
    setJoinLoading(true);
    try {
      await orgAPI.join({ code: joinCode.trim() });
      toast.success('Joined organization successfully!');
      setJoinCode('');
      await fetchUser();
      const res = await orgAPI.getMyOrg();
      setOrg(res.data.org);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to join organization.');
    } finally {
      setJoinLoading(false);
    }
  };

  const handleAddMember = async () => {
    if (!memberEmail.trim()) return;
    setAddMemberLoading(true);
    try {
      await orgAPI.addMember({ email: memberEmail.trim() });
      toast.success(`${memberEmail} added to organization!`);
      setMemberEmail('');
      const res = await orgAPI.listMembers();
      setMembers(res.data.members);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add member.');
    } finally {
      setAddMemberLoading(false);
    }
  };

  const handleFetchCode = async () => {
    setCodeLoading(true);
    try {
      const res = await orgAPI.getCode();
      setOrgCode(res.data.join_code);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to get code.');
    } finally {
      setCodeLoading(false);
    }
  };

  const handleRegenerateCode = async () => {
    setCodeLoading(true);
    try {
      const res = await orgAPI.regenerateCode();
      setOrgCode(res.data.join_code);
      toast.success('Join code regenerated!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to regenerate code.');
    } finally {
      setCodeLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(orgCode);
    toast.success('Code copied to clipboard!');
  };

  const handleFetchMembers = async () => {
    try {
      const res = await orgAPI.listMembers();
      setMembers(res.data.members);
      setShowMembers(!showMembers);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to fetch members.');
    }
  };

  const handleRemoveMember = async (userId, userName) => {
    try {
      await orgAPI.removeMember(userId);
      toast.success(`${userName} removed from organization.`);
      const res = await orgAPI.listMembers();
      setMembers(res.data.members);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to remove member.');
    }
  };

  const handleLeaveOrg = async () => {
    setShowLeaveConfirm(false);
    try {
      await orgAPI.leave();
      toast.success('You have left the organization.');
      setOrg(null);
      setMembers([]);
      setShowOrgSection(false);
      setShowMembers(false);
      await fetchUser();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to leave organization.');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/portal/login');
    toast.success('Logged out successfully');
  };

  const closeSidebar = () => setSidebarOpen(false);

  const isClient = hasRole('client');

  const allNavItems = isClient ? [
    { module: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/portal/dashboard', testId: 'nav-dashboard' },
    { module: 'services', label: 'Services', icon: Package, path: '/portal/services', testId: 'nav-services' },
    { module: 'review', label: 'Review', icon: Upload, path: '/portal/review', testId: 'nav-review', badge: cartCount },
    { module: 'history', label: 'History', icon: History, path: '/portal/history', testId: 'nav-history' },
    { module: 'payments', label: 'Payments', icon: CreditCard, path: '/portal/payments', testId: 'nav-payments' },
    { module: 'wallet', label: 'Wallet', icon: Wallet, path: '/portal/wallet', testId: 'nav-wallet' },
    { module: 'tickets', label: 'Support', icon: LifeBuoy, path: '/portal/tickets', testId: 'nav-tickets' },
  ] : [
    { module: 'dashboard', label: 'Dashboard', icon: Shield, path: '/portal/admin/dashboard', testId: 'nav-admin-dashboard', perm: 'dashboard.view' },
    { module: 'my_tasks', label: 'My Tasks', icon: ListChecks, path: '/portal/admin/my-tasks', testId: 'nav-my-tasks', badge: pendingCount, perm: 'orders.view_assigned' },
    { module: 'team_tasks', label: 'Team Tasks', icon: Users, path: '/portal/admin/team-tasks', testId: 'nav-team-tasks', perm: 'workflow.team_tasks' },
    { module: 'admin_users', label: 'Admin Users', icon: Shield, path: '/portal/admin/users', testId: 'nav-admin-users', perm: 'users.view' },
    { module: 'admin_services', label: 'Services', icon: Package, path: '/portal/admin/services', testId: 'nav-admin-services', perm: 'services.manage' },
    { module: 'organizations', label: 'Organizations', icon: Building, path: '/portal/admin/organizations', testId: 'nav-admin-orgs', perm: 'organizations.view' },
    { module: 'clients', label: 'Clients', icon: Users, path: '/portal/admin/clients', testId: 'nav-clients', perm: 'clients.view' },
    { module: 'jobs', label: 'Manage Jobs', icon: Briefcase, path: '/portal/admin/jobs', testId: 'nav-admin-jobs', perm: 'orders.view_all' },
    { module: 'workflow', label: 'Workflow Queue', icon: GitPullRequest, path: '/portal/admin/workflow', testId: 'nav-workflow', perm: 'workflow.view' },
    { module: 'review', label: 'Review Section', icon: ClipboardCheck, path: '/portal/admin/review', testId: 'nav-admin-review', perm: 'documents.review' },
    { module: 'payments', label: 'Payments', icon: CreditCard, path: '/portal/admin/payments', testId: 'nav-admin-payments', perm: 'payments.view' },
    { module: 'escalations', label: 'Escalations', icon: AlertTriangle, path: '/portal/admin/escalations', testId: 'nav-escalations', perm: 'workflow.escalate' },
  ];

  const navItems = allNavItems.filter(item => {
    if (isClient) return true;
    if (hasRole('super_admin')) return true;
    return item.perm ? hasPermission(item.perm) : true;
  });

  return (
    <>
      <button
        className="fixed top-3 left-3 z-50 lg:hidden bg-slate-900 text-white p-2 rounded-lg shadow-lg hover:bg-slate-800 transition-all active:scale-95"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <XIcon size={18} /> : <MenuIcon size={18} />}
      </button>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden animate-in fade-in duration-200"
          onClick={closeSidebar}
        />
      )}

      <div className={`
        w-64 bg-slate-900 text-white flex flex-col h-screen shrink-0 overflow-hidden
        fixed inset-y-0 left-0 z-40
        shadow-2xl
        transition-transform duration-300 ease-in-out
        lg:relative lg:translate-x-0 lg:shadow-none
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <img src="/images/logo.png" alt="TBR Solutions" className="h-10" />
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-6 space-y-2 overflow-y-auto min-h-0">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={closeSidebar}
                onMouseEnter={() => handleNavHover(item.path)}
                className={`flex items-center space-x-3 px-4 py-3 rounded transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
                data-testid={item.testId}
              >
                <Icon size={20} />
                <span className="flex-1">{item.label}</span>
                {item.badge != null && item.badge > 0 && (
                  <span className="min-w-[1.25rem] h-5 flex items-center justify-center bg-red-500 text-white text-xs font-bold rounded-full px-1">
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Info & Organization & Logout */}
        <div className="p-4 border-t border-slate-800 space-y-3">
          <div>
            <p className="text-xs text-slate-400 mb-1">Signed in as</p>
            <p className="text-sm font-medium text-white truncate">{user?.email}</p>
            <p className="text-xs text-slate-400 mt-1 capitalize">{user?.role?.replace('_', ' ')}</p>
          </div>

          {/* Organization Section */}
          {!orgLoading && (
            <div className="border-t border-slate-700 pt-3">
              {org ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Building size={14} className="text-slate-400 shrink-0" />
                    <span className="text-sm text-white truncate font-medium">{org.name}</span>
                    <span className="text-[10px] uppercase text-slate-500 ml-auto">{org.org_role}</span>
                  </div>

                  <div className="space-y-2">
                      <button
                        onClick={() => { setShowOrgSection(!showOrgSection); if (!showOrgSection) handleFetchCode(); }}
                        className="text-xs text-blue-400 hover:text-blue-300"
                      >
                        {showOrgSection ? 'Hide' : 'Manage'} Organization
                      </button>

                      {showOrgSection && (
                        <div className="space-y-2 bg-slate-800 rounded p-2">
                          <div className="flex items-center gap-1">
                                <code className="text-xs bg-slate-900 px-2 py-1 rounded text-yellow-400 flex-1 truncate font-mono">
                                  {codeLoading ? '...' : orgCode}
                                </code>
                                {orgCode && (
                                  <>
                                    <button onClick={handleCopyCode} className="text-slate-400 hover:text-white p-1" title="Copy">
                                      <Copy size={12} />
                                    </button>
                                    <button onClick={handleRegenerateCode} className="text-slate-400 hover:text-white p-1" title="Regenerate">
                                      <RefreshCw size={12} />
                                    </button>
                                  </>
                                )}
                              </div>

                          {/* Add Member */}
                          <div className="flex gap-1">
                            <Input
                              value={memberEmail}
                              onChange={(e) => setMemberEmail(e.target.value)}
                              placeholder="Email to add"
                              className="h-7 text-xs bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                            />
                            <Button
                              size="sm"
                              className="h-7 px-2 shrink-0"
                              onClick={handleAddMember}
                              disabled={addMemberLoading || !memberEmail.trim()}
                            >
                              <UserPlus size={12} />
                            </Button>
                          </div>

                          {/* Members */}
                          <button
                            onClick={handleFetchMembers}
                            className="text-xs text-slate-400 hover:text-white"
                          >
                            {showMembers ? 'Hide' : 'View'} Members ({members.length})
                          </button>
                          {showMembers && members.length > 0 && (
                            <div className="max-h-24 overflow-y-auto space-y-1">
                              {members.map((m) => (
                                <div key={m.id} className="flex items-center gap-1 group">
                                  <p className="text-xs text-slate-400 truncate flex-1">
                                    {m.full_name || m.email}
                                    <span className="text-slate-600 ml-1">({m.org_role})</span>
                                  </p>
                                  {m.id !== user?.id && org?.org_role === 'admin' && (
                                    <button
                                      onClick={() => handleRemoveMember(m.id, m.full_name || m.email)}
                                      className="text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-opacity p-0.5"
                                      title="Remove from organization"
                                    >
                                      <Trash2 size={12} />
                                    </button>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Leave Organization */}
                          <button
                            onClick={() => setShowLeaveConfirm(true)}
                            className="text-xs text-red-400 hover:text-red-300 pt-1"
                          >
                            Leave Organization
                          </button>
                        </div>
                      )}
                    </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-xs text-slate-500">You are not part of an organization yet.</p>
                  {/* Join Org */}
                  <div className="flex gap-1">
                    <Input
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      placeholder="Enter join code"
                      className="h-7 text-xs bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                    />
                    <Button
                      size="sm"
                      className="h-7 px-2 shrink-0"
                      onClick={handleJoinOrg}
                      disabled={joinLoading || !joinCode.trim()}
                    >
                      Join
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          <Button
            variant="outline"
            className="w-full border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
            onClick={handleLogout}
            data-testid="logout-button"
          >
            <LogOut size={16} className="mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <Dialog open={showLeaveConfirm} onOpenChange={setShowLeaveConfirm}>
        <DialogContent className="sm:max-w-[380px]">
          <DialogHeader>
            <DialogTitle>Leave Organization</DialogTitle>
            <DialogDescription>
              Are you sure you want to leave <span className="font-medium text-foreground">{org?.name}</span>? You'll need a join code to rejoin.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setShowLeaveConfirm(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleLeaveOrg}>
              Leave
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default PortalSidebar;