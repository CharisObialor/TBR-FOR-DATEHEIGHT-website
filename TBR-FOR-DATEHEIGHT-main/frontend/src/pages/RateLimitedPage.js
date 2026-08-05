import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Clock, Home } from 'lucide-react';

const RateLimitedPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          <Clock className="w-16 h-16 text-yellow-500" />
        </div>
        <h1 className="text-6xl font-bold text-foreground mb-2">429</h1>
        <h2 className="text-xl font-semibold text-foreground mb-4">Too many requests</h2>
        <p className="text-muted-foreground mb-8">
          You have made too many requests in a short period. Please wait a moment before trying again.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" onClick={() => window.location.reload()}>
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

export default RateLimitedPage;
