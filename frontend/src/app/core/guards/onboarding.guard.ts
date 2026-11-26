// Onboarding guard — redirects users who haven't set up a profile
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { ProfileService } from '../services/profile.service';
import { map, catchError, of } from 'rxjs';

export const onboardingGuard: CanActivateFn = () => {
  const profile = inject(ProfileService);
  const router = inject(Router);

  return profile.getProfile().pipe(
    map(p => p ? true : router.createUrlTree(['/onboarding'])),
    catchError(() => of(router.createUrlTree(['/onboarding'])))
  );
};

