import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ShieldOff, Home, ArrowLeft } from 'lucide-react';

const ForbiddenPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          <ShieldOff className="w-16 h-16 text-red-500" />
        </div>
        <h1 className="text-6xl font-bold text-foreground mb-2">403</h1>
        <h2 className="text-xl font-semibold text-foreground mb-4">Access denied</h2>
        <p className="text-muted-foreground mb-8">
          You do not have permission to access this page. Please contact your administrator if you believe this is a mistake.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" onClick={() => window.history.back()}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
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

export default ForbiddenPage;
