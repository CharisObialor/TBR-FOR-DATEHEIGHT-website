import React from 'react';
import PortalSidebar from './PortalSidebar';

const PortalLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-50">
      <PortalSidebar />
      <div className="flex-1 overflow-y-auto min-w-0">
        <div className="px-4 py-4 sm:px-6 sm:py-6 lg:p-8 pt-14 lg:pt-8">
          {children}
        </div>
      </div>
    </div>
  );
};

export default PortalLayout;
