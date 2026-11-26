// Auth guard — allows instant access with guest auto-session if unauthenticated
import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  if (!auth.token) {
    localStorage.setItem('access_token', 'cleanair-session-' + Date.now());
  }
  return true;
};
