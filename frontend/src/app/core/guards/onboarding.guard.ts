// Onboarding guard — allows browsing with fallback profile
import { CanActivateFn } from '@angular/router';

export const onboardingGuard: CanActivateFn = () => {
  return true;
};
