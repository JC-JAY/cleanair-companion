import { Component, inject, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatStepperModule } from '@angular/material/stepper';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { switchMap } from 'rxjs';

import { AuthService } from '../../core/services/auth.service';
import { ProfileService } from '../../core/services/profile.service';

@Component({
  selector: 'ca-onboarding',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatStepperModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="onboarding-wrapper">
      <mat-card>
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">eco</mat-icon>
          <mat-card-title>{{ 'onboarding.title' | translate }}</mat-card-title>
          <mat-card-subtitle>{{ 'onboarding.subtitle' | translate }}</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <mat-stepper [linear]="true" #stepper>
            <!-- Step 1: Location -->
            <mat-step [stepControl]="locationForm">
              <form [formGroup]="locationForm">
                <ng-template matStepLabel>{{ 'onboarding.step1' | translate }}</ng-template>
                <div class="step-fields">
                  <button mat-stroked-button type="button" color="primary" (click)="useGPS()">
                    <mat-icon>my_location</mat-icon>
                    {{ 'onboarding.useGPS' | translate }}
                  </button>
                  <mat-form-field appearance="outline">
                    <mat-label>City</mat-label>
                    <input matInput formControlName="city" placeholder="e.g. Pune">
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>State</mat-label>
                    <input matInput formControlName="state">
                  </mat-form-field>
                </div>
                <div class="step-actions">
                  <button mat-raised-button color="primary" matStepperNext>
                    {{ 'onboarding.next' | translate }}
                  </button>
                </div>
              </form>
            </mat-step>

            <!-- Step 2: Household -->
            <mat-step [stepControl]="householdForm">
              <form [formGroup]="householdForm">
                <ng-template matStepLabel>{{ 'onboarding.step2' | translate }}</ng-template>
                <div class="step-fields">
                  <mat-form-field appearance="outline">
                    <mat-label>Household size</mat-label>
                    <input matInput type="number" formControlName="household_size" min="1" max="20">
                  </mat-form-field>
                  <mat-checkbox formControlName="has_children">Children in household</mat-checkbox>
                  <mat-checkbox formControlName="has_elderly">Elderly members (60+)</mat-checkbox>
                  <mat-checkbox formControlName="has_asthma_respiratory">Asthma or respiratory conditions</mat-checkbox>
                  <mat-checkbox formControlName="has_pregnancy">Pregnant member</mat-checkbox>
                </div>
                <div class="step-actions">
                  <button mat-button matStepperPrevious>{{ 'onboarding.back' | translate }}</button>
                  <button mat-raised-button color="primary" matStepperNext>{{ 'onboarding.next' | translate }}</button>
                </div>
              </form>
            </mat-step>

            <!-- Step 3: Home & Commute -->
            <mat-step [stepControl]="homeForm">
              <form [formGroup]="homeForm">
                <ng-template matStepLabel>{{ 'onboarding.step3' | translate }}</ng-template>
                <div class="step-fields">
                  <mat-form-field appearance="outline">
                    <mat-label>Home type</mat-label>
                    <mat-select formControlName="home_type">
                      <mat-option value="apartment">Apartment</mat-option>
                      <mat-option value="house">Independent House</mat-option>
                      <mat-option value="other">Other</mat-option>
                    </mat-select>
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Cooking fuel</mat-label>
                    <mat-select formControlName="cooking_fuel">
                      <mat-option value="lpg">LPG Cylinder</mat-option>
                      <mat-option value="piped_gas">Piped Gas</mat-option>
                      <mat-option value="induction">Induction / Electric</mat-option>
                      <mat-option value="biomass">Biomass / Wood</mat-option>
                      <mat-option value="kerosene">Kerosene</mat-option>
                    </mat-select>
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>Primary commute mode</mat-label>
                    <mat-select formControlName="commute_mode">
                      <mat-option value="two_wheeler_petrol">Two-wheeler (Petrol)</mat-option>
                      <mat-option value="two_wheeler_electric">Two-wheeler (Electric)</mat-option>
                      <mat-option value="car_petrol">Car (Petrol)</mat-option>
                      <mat-option value="car_diesel">Car (Diesel)</mat-option>
                      <mat-option value="car_cng">Car (CNG)</mat-option>
                      <mat-option value="bus">Bus</mat-option>
                      <mat-option value="metro">Metro</mat-option>
                      <mat-option value="auto">Auto-rickshaw</mat-option>
                      <mat-option value="walk">Walk</mat-option>
                      <mat-option value="cycle">Cycle</mat-option>
                      <mat-option value="wfh">Work from home</mat-option>
                    </mat-select>
                  </mat-form-field>
                  <mat-form-field appearance="outline">
                    <mat-label>One-way commute distance (km)</mat-label>
                    <input matInput type="number" formControlName="commute_distance_km" min="0" max="200">
                  </mat-form-field>
                  <mat-checkbox formControlName="has_kitchen_exhaust">Kitchen exhaust fan available</mat-checkbox>
                </div>
                <div class="step-actions">
                  <button mat-button matStepperPrevious>{{ 'onboarding.back' | translate }}</button>
                  <button mat-raised-button color="primary" matStepperNext>{{ 'onboarding.next' | translate }}</button>
                </div>
              </form>
            </mat-step>

            <!-- Step 4: Devices & Budget -->
            <mat-step [stepControl]="devicesForm">
              <form [formGroup]="devicesForm">
                <ng-template matStepLabel>{{ 'onboarding.step4' | translate }}</ng-template>
                <div class="step-fields">
                  <mat-form-field appearance="outline">
                    <mat-label>Budget level</mat-label>
                    <mat-select formControlName="budget_level">
                      <mat-option value="low">Low / Free hacks first</mat-option>
                      <mat-option value="medium">Medium</mat-option>
                      <mat-option value="high">High</mat-option>
                    </mat-select>
                  </mat-form-field>
                  <mat-checkbox formControlName="has_purifier">Air purifier</mat-checkbox>
                  <mat-checkbox formControlName="has_mask">N95 / KN95 masks</mat-checkbox>
                  <mat-checkbox formControlName="has_plants">Indoor plants</mat-checkbox>
                  <mat-checkbox formControlName="has_fans">Table / exhaust fans</mat-checkbox>
                </div>
                <div class="step-actions">
                  <button mat-button matStepperPrevious>{{ 'onboarding.back' | translate }}</button>
                  <button mat-raised-button color="primary" [disabled]="saving()" (click)="submit()">
                    {{ 'onboarding.finish' | translate }}
                  </button>
                </div>
              </form>
            </mat-step>
          </mat-stepper>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .onboarding-wrapper { max-width: 720px; margin: 16px auto; }
    .step-fields { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }
    .step-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px; }
  `],
})
export class OnboardingComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private profileSvc = inject(ProfileService);
  private router = inject(Router);

  saving = signal(false);

  locationForm = this.fb.group({
    latitude: [18.52],
    longitude: [73.85],
    city: ['Pune', Validators.required],
    state: ['Maharashtra', Validators.required],
  });

  householdForm = this.fb.group({
    household_size: [2, [Validators.required, Validators.min(1)]],
    has_children: [false],
    has_elderly: [false],
    has_asthma_respiratory: [false],
    has_pregnancy: [false],
  });

  homeForm = this.fb.group({
    home_type: ['apartment'],
    cooking_fuel: ['lpg'],
    has_kitchen_exhaust: [false],
    commute_mode: ['two_wheeler_petrol'],
    commute_distance_km: [10],
  });

  devicesForm = this.fb.group({
    budget_level: ['medium'],
    has_purifier: [false],
    has_mask: [false],
    has_plants: [false],
    has_fans: [true],
  });

  useGPS() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(pos => {
      this.locationForm.patchValue({
        latitude: Number(pos.coords.latitude.toFixed(2)),
        longitude: Number(pos.coords.longitude.toFixed(2)),
      });
    });
  }

  submit() {
    if (this.saving()) return;
    this.saving.set(true);

    const devices: string[] = [];
    const d = this.devicesForm.value;
    if (d.has_purifier) devices.push('purifier');
    if (d.has_mask) devices.push('n95_mask');
    if (d.has_plants) devices.push('plants');
    if (d.has_fans) devices.push('fans');

    const payload = {
      ...this.locationForm.value,
      ...this.householdForm.value,
      ...this.homeForm.value,
      budget_level: d.budget_level || 'medium',
      available_devices: devices,
    };

    const ensureAuth$ = this.auth.token
      ? this.profileSvc.createProfile(payload as any)
      : this.auth.createAnonymousSession().pipe(
          switchMap(() => this.profileSvc.createProfile(payload as any))
        );

    ensureAuth$.subscribe({
      next: () => {
        this.saving.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.saving.set(false);
      },
    });
  }
}

