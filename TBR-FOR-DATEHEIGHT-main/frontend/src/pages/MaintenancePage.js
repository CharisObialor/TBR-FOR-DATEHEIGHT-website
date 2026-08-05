import React from 'react';
import { Button } from '../components/ui/button';
import { Wrench, RefreshCw } from 'lucide-react';

const MaintenancePage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          <Wrench className="w-16 h-16 text-purple-500" />
        </div>
        <h1 className="text-6xl font-bold text-foreground mb-2">503</h1>
        <h2 className="text-xl font-semibold text-foreground mb-4">Under maintenance</h2>
        <p className="text-muted-foreground mb-8">
          We are currently performing scheduled maintenance. We will be back shortly.
        </p>
        <Button variant="outline" onClick={() => window.location.reload()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Check Again
        </Button>
      </div>
    </div>
  );
};

export default MaintenancePage;
