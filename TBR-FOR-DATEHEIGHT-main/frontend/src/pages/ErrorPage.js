import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { AlertTriangle, Home, RefreshCw, ArrowLeft } from 'lucide-react';

const ErrorPage = ({ status = 500, title = 'Something went wrong', message = 'An unexpected error occurred. Please try again later.' }) => {
  const navigate = useNavigate();

  const icons = {
    400: <AlertTriangle className="w-16 h-16 text-amber-500" />,
    403: <AlertTriangle className="w-16 h-16 text-red-500" />,
    404: <AlertTriangle className="w-16 h-16 text-orange-500" />,
    429: <AlertTriangle className="w-16 h-16 text-yellow-500" />,
    500: <AlertTriangle className="w-16 h-16 text-red-600" />,
    503: <AlertTriangle className="w-16 h-16 text-purple-500" />,
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="flex justify-center mb-6">
          {icons[status] || icons[500]}
        </div>
        <h1 className="text-6xl font-bold text-foreground mb-2">{status}</h1>
        <h2 className="text-xl font-semibold text-foreground mb-4">{title}</h2>
        <p className="text-muted-foreground mb-8">{message}</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>
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

export default ErrorPage;
