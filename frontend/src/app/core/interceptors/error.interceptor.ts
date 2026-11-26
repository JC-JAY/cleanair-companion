// Error interceptor — handles 401 (logout), 503 (offline), and global errors
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        auth.logout();
      } else if (error.status === 0 || error.status === 503) {
        // Network error — PWA will serve cached data
        console.warn('Network unavailable — serving offline data');
      }
      return throwError(() => error);
    })
  );
};

