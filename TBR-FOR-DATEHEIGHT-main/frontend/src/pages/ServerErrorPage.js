import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

const ServerErrorPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          <AlertTriangle className="w-16 h-16 text-red-600" />
        </div>
        <h1 className="text-6xl font-bold text-foreground mb-2">500</h1>
        <h2 className="text-xl font-semibold text-foreground mb-4">Internal server error</h2>
        <p className="text-muted-foreground mb-8">
          Something went wrong on our end. Our team has been notified and we are working on a fix.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" onClick={() => window.location.reload()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
          <Link to="/">
            <Button>
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ServerErrorPage;
